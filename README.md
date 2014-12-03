**Required configuration for this application**

Copy environment_private.sh.git  to environment_private.sh in the root of the project and set the following environment variables:

```
cp environment_private.sh.git  environment_private.sh
```

Then in environment.sh set the following:

```
export REGISTRY_CONSUMER_KEY='some key'
export REGISTRY_CONSUMER_SECRET='some secret'
```

To generate values for the above, use the management command register-service in: [registry](https://github.com/sausages-of-the-future/registry)


**Deploy to heroku**

Make sure you have [installed the heroku toolbelt](https://toolbelt.heroku.com/)

*Note if you add anthing to environment.sh or environment_private.sh then add those config items to the heroku app as well*

For example
```
heroku config:set SETTINGS='config.Config'

```

If you make changes, push to github first and then push to heroku master

To set up heroku master as a remote :

```
heroku git:remote -a fishing-gov
```

The you can:

```
git push heroku master
```

But again, please make sure your changes are in github master first. Then all will be synced up nicely
