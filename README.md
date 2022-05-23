CONVINT 
=======

## Vision


---
## API Documentation


## Mockup

## API Spec
The preferred JSON object to be returned by the API should be structured as follows:

### Users (for authentication)

```source-json
{
  "user": {
    "email": "convint@convint.com",
    "token": "jwt.token.here",
    "username": "convint",
    "bio": "Software Engineer at work!",
    "image": null
  }
}
```
### Profile
```source-json
{
  "profile": {
    "username": "convint",
    "bio": "Software Engineer at work!",
    "image": "image-link",
    "following": false
  }
}
```
### Single Article
```source-json
{
  "article": {
    "slug": "how-to-setup-a-django-project",
    "title": "How to setup a django project",
    "description": "Where do you start from?",
    "body": "Checkout the docs!!",
    "tagList": ["django", "setup"],
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:48:35.824Z",
    "favorited": false,
    "favoritesCount": 0,
    "author": {
      "username": "convint",
      "bio": "Software Engineer at work!",
      "image": "https://....",
      "following": false
    }
  }
}
```
### Multiple Articles
```source-json
{
  "articles":[{
    "slug": "how-to-setup-a-django-project",
    "title": "How to setup a django project",
    "description": "Where do you start from?",
    "body": "Checkout the docs!!",
    "tagList": ["django", "setup"],
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:48:35.824Z",
    "favorited": false,
    "favoritesCount": 0,
    "author": {
      "username": "convint",
      "bio": "Software Engineer at work!",
      "image": "https://....",
      "following": false
    }
  }, {

    "slug": "how-to-setup-a-django-project",
    "title": "How to setup a django project",
    "description": "Where do you start from?",
    "body": "Checkout the docs!!",
    "tagList": ["django", "setup"],
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:48:35.824Z",
    "favorited": false,
    "favoritesCount": 0,
    "author": {
      "username": "convint",
      "bio": "Software Engineer at work!",
      "image": "https://....",
      "following": false
    }
  }],
  "articlesCount": 2
}
```
### Single Comment
```source-json
{
  "comment": {
    "id": 1,
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:22:56.637Z",
    "body": "It takes a Jacobian",
    "author": {
      "username": "convint",
      "bio": "I work at statefarm",
      "image": "https://i.stack.imgur.com/xHWG8.jpg",
      "following": false
    }
  }
}
```
### Multiple Comments
```source-json
{
  "comments": [{
    "id": 1,
    "createdAt": "2016-02-18T03:22:56.637Z",
    "updatedAt": "2016-02-18T03:22:56.637Z",
    "body": "It takes a Jacobian",
    "author": {
      "username": "convint",
      "bio": "Software Engineer at work!",
      "image": "https://i.stack.imgur.com/xHWG8.jpg",
      "following": false
    }
  }],
  "commentsCount": 1
}
```
### List of Tags
```source-json
{
  "tags": [
    "reactjs",
    "python"
  ]
}
```
### Errors and Status Codes
If a request fails any validations, expect errors in the following format:

```source-json
{
  "errors":{
    "body": [
      "can't be empty"
    ]
  }
}
```
### Other status codes:
401 for Unauthorized requests, when a request requires authentication but it isn't provided

403 for Forbidden requests, when a request may be valid but the user doesn't have permissions to perform the action

404 for Not found requests, when a resource can't be found to fulfill the request


Endpoints:
----------

### Authentication:

`POST /api/users/login`

Example request body:

```source-json
{
  "user":{
    "email": "convint@convint.com",
    "password": "convint@123"
  }
}
```

No authentication required, returns a User

Required fields: `email`, `password`

### Registration:

`POST /api/users`

Example request body:

```source-json
{
  "user":{
    "username": "Convint",
    "email": "convint@convint.com",
    "password": "convint@123"
  }
}
```

No authentication required, returns a User

Required fields: `email`, `username`, `password`

### Get Current User

`GET /api/user`

Authentication required, returns a User that's the current user

### Update User

`PUT /api/user`

Example request body:

```source-json
{
  "user":{
    "email": "convint@convint.com",
    "bio": "Software Engineer at work!",
    "image": "https://...."
  }
}
```

Authentication required, returns the User

Accepted fields: `email`, `username`, `password`, `image`, `bio`

### Get Profile

`GET /api/profiles/:username`

Authentication optional, returns a Profile

### Follow user

`POST /api/profiles/:username/follow`

Authentication required, returns a Profile

No additional parameters required

### Unfollow user

`DELETE /api/profiles/:username/follow`

Authentication required, returns a Profile

No additional parameters required

### List Articles

`GET /api/articles`

Returns most recent articles globally by default, provide `tag`, `author` or `favorited` query parameter to filter results

Query Parameters:

Filter by tag:

`?tag=python`

Filter by author:

`?author=convint`

Favorited by user:

`?favorited=convint`

Limit number of articles (default is 20):

`?limit=20`

Offset/skip number of articles (default is 0):

`?offset=0`

Authentication optional, will return multiple articles, ordered by most recent first

### Feed Articles

`GET /api/articles/feed`

Can also take `limit` and `offset` query parameters like List Articles

Authentication required, will return multiple articles created by followed users, ordered by most recent first.

### Get Article

`GET /api/articles/:slug`

No authentication required, will return single article

### Create Article

`POST /api/articles`

Example request body:

```source-json
{
  "article": {
    "title": "How to.. ",
    "description": "Ever wonder how?",
    "body": "You have to..",
    "tagList": ["reactjs", "django"]
  }
}
```

Authentication required, will return an Article

Required fields: `title`, `description`, `body`

Optional fields: `tagList` as an array of Strings

### Update Article

`PUT /api/articles/:slug`

Example request body:

```source-json
{
  "article": {
    "title": "Did you setup your project?"
  }
}
```

Authentication required, returns the updated Article

Optional fields: `title`, `description`, `body`

The `slug` also gets updated when the `title` is changed

### Delete Article

`DELETE /api/articles/:slug`

Authentication required

### Add Comments to an Article

`POST /api/articles/:slug/comments`

Example request body:

```source-json
{
  "comment": {
    "body": "Looks good!"
  }
}
```

Authentication required, returns the created Comment
Required field: `body`

### Get Comments from an Article

`GET /api/articles/:slug/comments`

Authentication optional, returns multiple comments

### Delete Comment

`DELETE /api/articles/:slug/comments/:id`

Authentication required

### Favorite Article

`POST /api/articles/:slug/favorite`

Authentication required, returns the Article
No additional parameters required

### Unfavorite Article

`DELETE /api/articles/:slug/favorite`

Authentication required, returns the Article

No additional parameters required

### Get Tags

`GET /api/tags`
