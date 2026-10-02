#!/usr/bin/env python3
"""One opt-in OAM-S deterministic OEQ method bridge; no weight/model math changes."""

import types

from nequip.data import AtomicDataDict
from openequivariance import TensorProductConv


def _deterministic_scatter_forward(self, x, edge_attr, edge_weight, edge_dst, edge_src, sender_perm):
    # The packaged OpenEquivarianceTensorProductScatter.forward is identical
    # except for passing the source-required sixth permutation argument.
    return self.tp_conv(
        x.to(self.model_dtype),
        edge_attr.to(self.model_dtype),
        edge_weight.to(self.model_dtype),
        edge_dst,
        edge_src,
        sender_perm,
    )


def _deterministic_interaction_forward(self, data):
    # Exact packaged 0.15 InteractionBlock.forward dataflow, with only the
    # shared edge_transpose_perm threaded to tp_scatter.
    if AtomicDataDict.LMP_MLIAP_DATA_KEY in data:
        num_local_nodes = self._get_mliap_num_local(data)
    else:
        num_local_nodes = AtomicDataDict.num_nodes(data)
    x = data[AtomicDataDict.NODE_FEATURES_KEY]
    if not self.is_first_layer:
        x = x[:num_local_nodes]
    if self.sc is not None:
        node_attrs = data[AtomicDataDict.NODE_ATTRS_KEY]
        if not self.is_first_layer:
            node_attrs = node_attrs[:num_local_nodes]
        sc = self.sc(x, node_attrs)
    x = self.linear_1(x)
    alpha = self.scatter_norm_factor
    if alpha is not None:
        x = alpha * x
    if not self.is_first_layer:
        data[AtomicDataDict.NODE_FEATURES_KEY] = x
        data = self.ghost_exchange(data, ghost_included=False)
        x = data[AtomicDataDict.NODE_FEATURES_KEY]
    x = self.tp_scatter(
        x=x,
        edge_attr=data[AtomicDataDict.EDGE_ATTRS_KEY],
        edge_weight=self.edge_mlp(data[AtomicDataDict.EDGE_EMBEDDING_KEY]),
        edge_dst=data[AtomicDataDict.EDGE_INDEX_KEY][0],
        edge_src=data[AtomicDataDict.EDGE_INDEX_KEY][1],
        sender_perm=data[AtomicDataDict.EDGE_TRANSPOSE_PERM_KEY],
    )[:num_local_nodes]
    x = self.linear_2(x)
    if self.sc is not None:
        x = x + sc
    data[AtomicDataDict.NODE_FEATURES_KEY] = x
    return data


def enable_deterministic_oeq_for_packaged_oam_s(model):
    """Modify only the two officially OEQ-enabled OAM-S interaction modules."""
    blocks = [(name, module) for name, module in model.named_modules() if type(module).__name__ == "InteractionBlock"]
    if len(blocks) != 2:
        raise RuntimeError(f"Expected exactly two OAM-S InteractionBlock modules, got {[n for n, _ in blocks]}")
    receipts = []
    for name, block in blocks:
        scatter = block.tp_scatter
        if type(scatter).__name__ != "OpenEquivarianceTensorProductScatter":
            raise RuntimeError(f"{name} is not the official OEQ-modified scatter")
        old = scatter.tp_conv
        args = dict(old.input_args)
        if args.get("deterministic") is not False:
            raise RuntimeError("Official A0 OEQ consumer was not atomic")
        scatter.tp_conv = TensorProductConv(
            args["problem"],
            deterministic=True,
            kahan=args.get("kahan", False),
            torch_op=args["torch_op"],
            use_opaque=args["use_opaque"],
        )
        scatter.forward = types.MethodType(_deterministic_scatter_forward, scatter)
        block.forward = types.MethodType(_deterministic_interaction_forward, block)
        receipts.append({"block": name, "consumer_deterministic": True,
                         "same_TPProblem_object": scatter.tp_conv.input_args["problem"] is args["problem"],
                         "sender_perm_source": AtomicDataDict.EDGE_TRANSPOSE_PERM_KEY})
    return receipts
