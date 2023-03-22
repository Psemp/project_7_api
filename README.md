# Project 7 - API repo :

# 1 : Stack
- Django + Django Rest Framework + Streamlit
- PostgreSQL > 13 (13 in dev, 14 in production)
- Nginx served (HTTP only for now)
- Hosted on ubuntu server
- Using CDN for static files
- Full python requirements : requirements.txt (`pip install -r requirements.txt`)

# 2 : Template, styles
- Using boostrap + boostrap template to manage most of the CSS/JS. **[Core theme](https://startbootstrap.com/template/business-frontpage)**
- Default streamlit styles
- Statics served via CDN
- High contrast, colorblind friendly plots

# 3 : API guide
- Endpoints :
	- `host:port/api/predict/?client_id=<client_id>&model_id=<model_id>` : returns a prediction of the client defined by its id using a model defined by its idea. Shape of response if 200 : Base 100 score, local SHAP values, name of the variables

# 4 : Currently deployed at :
[51.159.155.177:80](http://51.159.155.177/)

# 5 : CI/CD managed by github actions
- Using Django build in test command to test routes and database actions

# 6 : Models :
- CatBoost and xGboost models trained and used can be found in the mlruns directory of this repo or [this repo](https://github.com/Psemp/ds_p7)