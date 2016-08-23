# Facebook Event API

This project is a small Python (Tornado) server that exposes a JSON API to describe
the public events hosted by the PyGre.io [Facebook page](https://facebook.com/pygre.io/events).

It is consumed by a front-end service in the PyGre.io main landing page, in the
calendar view of the upcoming courses.

Accessing the Facebook Graph API directly from the front-end would require to
publicly share the page access token (long-lived, therefore non-expiring), which
would cause security issues. The data exposed by this API is publicly visible
(even without a Facebook account), no names (of people attending or interested)
are sent in the JSON response.

## API Documentation:

```
HTTP/1.1 GET /

Response type: application/json
[
    {
        "id":           "0123456789",
        "name":         "Event Name",
        "description":  "Event description",
        "attending":    12,
        "interested":   42,
        "start_time":   "2016-07-23T15:00:00.0000Z",
        "end_time":     "2016-07-23T16:00:00.0000Z",        // optional
        "place": {
            "id":       "0123456789",
            "name":     "Holmes and Watson's",
            "location": {
                "street":       "221B Baker Street",
                "city":         "London",
                "zip":          "NW16XE",
                "latitude":     51.5237715,
                "longitude":    -0.1607272
            }
        }
    },
    {
        ...
    }
]
```

## Installation

* Clone the repository
* Install the requirements with pip
* Create a config.py file at the root of the working copy containing the following:

```
facebook_page_access_token = 'YourLongLivedAccessTokenPastedHere'
```
