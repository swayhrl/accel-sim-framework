from evidence import *
urls=[
('current_ogb_license.xml','https://s3.amazonaws.com/amazon-reviews-pds/license.txt'),
('ogb_official.html','https://ogb.stanford.edu/docs/nodeprop/'),
('wayback_cdx.json','https://web.archive.org/cdx/search/cdx?url=s3.amazonaws.com%2Famazon-reviews-pds%2Flicense.txt&output=json&filter=statuscode%3A200&filter=mimetype%3Atext%2Fplain&collapse=digest&filter=timestamp%3A202[0123].*&limit=3'),
('wayback_snapshot.txt','https://web.archive.org/web/20220101000000id_/https://s3.amazonaws.com/amazon-reviews-pds/license.txt'),
('aws_registry_candidates.json','https://api.github.com/repos/awslabs/open-data-registry/contents/datasets?ref=main'),
('aws_docs_history.json','https://api.github.com/repos/awslabs/open-data-docs/commits?path=docs/amazon-reviews-pds/license.txt&per_page=2'),
('ogb_license_issues.json','https://api.github.com/search/issues?q=repo%3Asnap-stanford%2Fogb%20products%20license&per_page=10'),
('publisher_dataset.html','https://cseweb.ucsd.edu/~jmcauley/datasets.html'),
('publisher_2014.html','https://jmcauley.ucsd.edu/data/amazon/'),
]
for name,url in urls:fetch(url,name,limit=1024**2)
