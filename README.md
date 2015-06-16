# Flags

Note: This doumentation is outdated and needs to be updated.

RESTful service for administering flags.
Reads and writes flags to/from a key-value store (currently Zookeeper) to be used to enable/disable features.
<br/>Can be used in any domain or application.

## Notions
### Flag
And sometimes also refered to as a key, is used to determine whether a certain feature is enabled or disabled, or it can also be used as a configuration value. for example: max number of listings per page... etc.

### Application
Each set of flags or keys are bound to a certain application domain, for example: mobile. This ensures isolation and prevents conflicts of flags in different domains.

## Authentication
Authentication of the application is done internally via Google Single Sign On, so in order to use it you need to authenticate yourself using dubizzle email account.

## Endpoints:

### Health checks:

* Nginx-level health check:
`GET http://{{host}}:{{port}}/check.txt`

* App-level health check:
`GET http://{{host}}:{{port}}/v1/check`


### Reading:

#### Read a single flag/key
`GET http://{{host}}:{{port}}/v1/flags/{{application}}/{{key/flag}}/`

> example:
`GET http://flags.dubizzlecloud.internal/v1/flags/mobile/ENABLE_CUPCAKES/`

Sample response:
* if the key does not exist:
```json
{
"ENABLE_CUPCAKES": null
}
```
* if the key exists, the value of the key will be returned:
```json
{
"ENABLE_CUPCAKES": 1
}
```

#### Get a list of all flags in a certain application
`GET http://{{host}}:{{port}}/v1/flags/{{application}}/`

> example:
`GET http://flags.dubizzlecloud.internal/v1/flags/mobile/`

<br/>Response:
<br/>**Code:**
`200 - OK`
<br/>**Content:**
```json
[
"TEST",
"ENABLE_CUPCAKES"
]
```


### Writing:

#### Create
* Create/Add a new flag to an application:
`POST http://{{host}}:{{port}}/v1/flags/{{application}}/{{key/flag}}/{{value}}/`

> example:
`POST http://flags.dubizzlecloud.internal/v1/flags/mobile/ENABLE_CUPCAKES/1/`

<br/>Response:
* if the key does not exist:
<br/>**Code:**
`201 - CREATED`
<br/>**Content:**
No response content

* if the key already exists:
<br/>**Code:**
`409 - CONFLICT`
<br/>**Content:**
`Key already exists! You might want to use PUT instead of POST.`

#### Update
* Update an existing flag:
`PUT http://{{host}}:{{port}}/v1/flags/{{application}}/{{key/flag}}/{{value}}/`

> example:
`PUT http://flags.dubizzlecloud.internal/v1/flags/mobile/ENABLE_CUPCAKES/2/`

<br/>Response:

* if the key to be updated was found:
<br/>**Code:**
`204 - NO CONTENT`
<br/>**Content:**
No content

* if the key does not exist:
<br/>**Code:**
`404 - NOT FOUND`
<br/>**Content:**
`Key does not exists! You might want to use POST instead of PUT.`

#### Delete
* Delete a flag from an application:
`DELETE http://{{host}}:{{port}}/v1/flags/{{application}}/{{key/flag}}/`

> example:
`DELETE http://flags.dubizzlecloud.internal/v1/flags/mobile/ENABLE_CUPCAKES/`

<br/>Response:

* if the key to be deleted was found:
<br/>**Code:**
`204 - NO CONTENT`
<br/>**Content:**
No content

* if the key does not exist:
<br/>**Code:**
`404 - NOT FOUND`
<br/>**Content:**
`Key does not exist!`


## What's next:
* Tests
* UI
* Reading the list of available applications
