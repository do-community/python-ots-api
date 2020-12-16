# Python One Time Secret API #

This API is for creating, storing, and sharing secrets. A user can securely store a secret with this API and send the passphrase and ID to a person who will be able to access the secret one time and one time only. The person creating the secret can also set an expiration time if the secret isn't viewed quickly enough. This is a remake of [onetimesecret.com](https://onetimesecret.com/).

**Note: Following these steps will result in charges for the use of DigitalOcean services**

## API Docs
All examples are using [`httpie`](https://httpie.org/). If you haven't checked 
it out you should.

Below are all of the public endpoints currently available.

### POST `/secrets`
Create a secret associated with a passphrase. Setting an experation time is 
optional.

*Parameters*

* `passphrase` (required) - The passphrase to access the secret.
* `message` (required) - The message to encrypt and store
* `expiration_time` - The amount of time in seconds before the secret expires.
Defaults to 604800 which is 1 week.

*Example*

`http POST https://example.api/secrets passphrase="hello sammy" message="Droplets are cool!" expiration_time=300`

*Returns 200*
```json
{
    "success": "True",
    "id": "<RANDOM_ID_ASSOCIATED_WITH_MESSAGE>"
}
```

*Returns 400*
```json
{
    "success": "False", 
    "message": "Missing passphrase and/or message"
}
```

### POST `/secrets/<ID_OF_MESSAGE>`
Retrieve the secret associated with an ID using a passphrase

*Parameters*

* `passphrase` (required) - The passphrase to access the secret.

*Example*

`http POST https://example.api/secrets/<ID_OF_MESSAGE> passphrase="hello sammy"`

*Returns 200*
```json
{
    "success": "True",
    "message": "<DECRYPTED_MESSAGE>"
}
```

*Returns 400*
```json
{
    "success": "False", 
    "message": "Missing passphrase"
}
```

*Returns 404*
```json
{
    "success": "False",
    "message": "This secret either never existed or it was already read",
}
```


## Requirements

* You need a DigitalOcean account. If you don't already have one, you can sign up at https://cloud.digitalocean.com/registrations/new
    
## Forking the Sample App Source Code

To use all the features of App Platform, you need to be running against your own copy of this application. To make a copy, click the Fork button above and follow the on-screen instructions. In this case, you'll be forking this repo as a starting point for your own app (see [Github documentation](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) to learn more about forking repos.

After forking the repo, you should now be viewing this README in your own github org (e.g. `https://github.com/<your-org>/python-ots-app`)

## Deploying the App ##

1. This app requires a Redis Database. You will need to setup one before deploying the app. If you don't already have one setup, check out [DigitalOcean's Managed Redis offering](https://www.digitalocean.com/docs/databases/redis/).
1. Visit https://cloud.digitalocean.com/apps (if you're not logged in, you may see an error message. Visit https://cloud.digitalocean.com/login directly and authenticate, then try again)
1. Click "Launch App" or "Create App"
1. Choose GitHub and authenticate with your GitHub credentials.
1. Under Repository, choose this repository (e.g. `<your-org>/python-ots-app`) and click **Next**.
1. On the next screen you will be prompted for the name of your app, which region you wish to deploy to, which branch you want deployments to spin off of and whether or not you wish to autodeploy the app every time an update is made to this branch. Fill this out according to how you want your app to function and click **Next**.
1. Modify the environment variables and add the following:
    1. `SALT` - Add a randomly generated string here to salt your encryption. You can generate one using a [random password generator](https://passwordsgenerator.net/).
    1. `DB_HOST` - The host name of the Redis Database.
    1. `DB_PORT` - The port the Redis Database is running on.
    1. `DB_PASSWORD` - The password to the Redis Database.
1. Modify the **Run Command** setting to point to your application. So the modified command would be `gunicorn --worker-tmp-dir /dev/shm --config gunicorn_config.py app:app`. 
1. There is no need to modify the **Build Command** section
1. Confirm your Plan settings and how many containers you want to launch and click **Launch Basic/Pro App**.
1. You should see a "Building..." progress indicator. And you can click "Deployments"→"Details" to see more details of the build.
1. It can currently take 5-6 minutes to build this app, so please be patient. Live build logs are coming soon to provide much more feedback during deployments.
1. Once the build completes successfully, click the "Live App" link in the header and you should see your running application in a new tab, displaying the home page.

## Making Changes to Your App ##

As long as you left the default Autodeploy option enabled when you first launched this app, you can now make code changes and see them automatically reflected in your live application. During these automatic deployments, your application will never pause or stop serving request because the App Platform offers zero-downtime deployments.

Here's an example code change you can make for this app:
1. Edit code within the repository
1. Commit the change to master. Normally it's a better practice to create a new branch for your change and then merge that branch to master after review, but for this demo you can commit to master directly.
1. Visit https://cloud.digitalocean.com/apps and navigate to your sample-python app.
1. You should see a "Building..." progress indicator, just like above.
1. Once the build completes successfully, click the "Live App" link in the header and you should see your updated application running. You may need to force refresh the page in your browser (e.g. using Shift+Reload).

## Learn More ##

You can learn more about the App Platform and how to manage and update your application at https://www.digitalocean.com/docs/apps/.


## Deleting the App #

When you no longer need this sample application running live, you can delete it by following these steps:
1. Visit the Apps control panel at https://cloud.digitalocean.com/apps
1. Navigate to the sample-python app
1. Choose "Settings"->"Destroy"
1. If you aren't using the Redis managed database anymore, be sure to delete it or you'll continue to incur charges.

This will delete the app and destroy any underlying DigitalOcean resources

**Note: If you don't delete your app or database, charges for the use of DigitalOcean services will continue to accrue.**
