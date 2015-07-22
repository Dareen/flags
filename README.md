# Flags

Feature toggles service based on dynamic segmentation and criteria.

Reads and writes flags configuration to/from a key-value store (currently Zookeeper) to be used to enable/disable features.

Can be used in multiple domains and applications e.g. Mobile, Motors, Property, Jobs, Core ... etc.

## Notions and terminology
#### Flag
And sometimes also refered to as a Key or as a Feature, it's used to determine whether a certain feature is enabled or disabled.

Future: to be used as a configuration value. e.g. max number of listings per view.

#### Application
Each set of features are bound to a certain application domain, e.g. Mobile, Motors, Property, Jobs, Core ... etc. This ensures isolation and prevents conflicts of flags in different domains.

#### Segmentation
A segmentation is how you would like to segment enabling or disabling your features. Can be by the user account type, or by the user device type, or both.
Example segmentations: platform, country.

#### Segmentation Option
Different types of a given segmentation, say platform segmentation, it has the following possible options: ios, androind, windows, blackberry ... etc.


## Authentication
Authentication of the admin UI is currently handled via a separate internal proxy, will support application authentication and authorization in the future.

## Endpoints

#### Health checks

* Nginx-level health check:

Endpoint: `GET http://{{host}}:{{port}}/check.txt`

Expected response:

```
HTTP/1.0 200 OK
```

* Application-level health check:

Endpoint: `GET http://{{host}}:{{port}}/v1/check`

Expected response:

```
HTTP/1.0 200 OK
Content-Type: text/html; charset=UTF-8

Up and running :)
```

#### Read all user-specific features (Basic mode)
This endpoint will return a list of all the features in an application, and whether they're enabled or disabled for the specified user segmentation in the get params.

Endpoint: `http://<host>/v1/api/<application>/basic/?<segment>=<option>`

Sample response:
```json
{
    "F1": true,
    "F2": true
}
```

#### Read all features configuration (Advanced)
This endpoint will return a list of all the features in an application, along with their full configuration, and also a "user_enabled" key which specifies whether a feature enabled or disabled for the specified user segmentation in the get params.

Endpoint: `http://<host>/v1/api/<application>/advanced/?<segment>=<option>`

Sample response:
```json
{
  "F1": {
    "segmentation": {
      "country": {
        "options": {
          "4": false,
          "7": false
        },
        "toggled": true
      },
      "platform": {
        "options": {
          "android": true,
          "ios": false
        },
        "toggled": true
      }
    },
    "user_enabled": false,
    "feature_toggled": true
  },
  "F2": {
    "segmentation": {
      "country": {
        "options": {
          "4": true,
          "7": true
        },
        "toggled": true
      },
      "platform": {
        "options": {
          "android": true,
          "ios": true
        },
        "toggled": true
      }
    },
    "user_enabled": true,
    "feature_toggled": true
  }
}
```

#### Read a user-specific feature (Basic)
Get a single feature in a basic parsed response
This endpoint will return whether a feature is enabled or disabled for the specified user segmentation in the get params.

Endpoint: `http://<host>/v1/api/<application>/basic/<feature>/?<segment>=<option>`

Sample response:
```json
{"F1": true}
```

#### Read a single feature's full configuration (Advanced)
This endpoint will return a single feature's full configuration, and also a "user_enabled" key which specifies whether that feature enabled or disabled for the specified user segmentation in the get params.

Endpoint: `http://<host>/v1/api/<application>/advanced/<feature>/?<segment>=<option>`

Sample response:
```json
{
  "segmentation": {
    "country": {
      "options": {
        "4": false,
        "7": false
      },
      "toggled": true
    },
    "platform": {
      "options": {
        "android": true,
        "ios": false
      },
      "toggled": true
    }
  },
  "user_enabled": true,
  "feature_toggled": true
}
```

## Setup
You can setup the application using [Docker](https://docker.com/):
* Install Docker
* After you clone the repo, inside the repo dir, run `make docker`
This will take care of all the setup, package installation and configuration needed for the application to run.
* Then after you build the docker container, run it providing your specific settings:
```bash
docker run -p 8095:80 -e NEW_RELIC_LICENSE_KEY="fake-key" -e PRODUCTION_MODE="0" -e SYSLOG_HOST="your-syslog-host" -e SYSLOG_PORT="your-syslog-port" -e VENV_DIR="python-virtualenv-dir-path" e REPO_DIR="dir-repo-path" -e APP_NAME="flags" -e ZK_HOSTS="comma-separated-ZK-hosts-and-ports" your-docker-image-here
```

## Monitoring
The application is integrated with [NewRelic](http://newrelic.com/) by default, just provide the account license key as a docker env var `NEW_RELIC_LICENSE_KEY` when you run the docker container, and enable `PRODUCTION_MODE`:
```bash
-e NEW_RELIC_LICENSE_KEY="your_license_key_here" -e PRODUCTION_MODE="1"
```

## What's next:
[list of improvements](https://github.com/dubizzle/flags/issues/7)
