<img src="doc_images/cortex-aengine_720.png" width="90px" height="50px">

## A. Brief description
- No siloes. Data can be streamed to whomever need it, whenever they need it.
- Infrastructure to collect, process, distribute to those who need the data, then embedding intelligence into that.
- Being able to see how the daily interactions and modifications to the data change things in the moment.

## B. Current Progress

[CLICK ME]( http://htmlpreview.github.io/?https://github.com/DIS-SIN/CORTEX/blob/master/cortex_mvp.html)

## C. MVP diagram

![Logical diagram](doc_images/Component.png)

![Physical diagram](doc_images/Deployment.png)

# C. Notes

mjolnir - tool for large data import: completed harvesting, normalization, and configuration for basic reference datasets to be imported into Jotunheimr via Yggdrasil:
+ Postal Code v2015 (Municipality, Community, Postal Code, Geo-Location, Province)
+ GoC Departments and Organizations from GEDS v2019 (en/fr names, abbreviations, sub-organization structure, locations)
+ GoC Occupation Classifications v2019 (occupation groups/sub-groups, classifications, levels)
