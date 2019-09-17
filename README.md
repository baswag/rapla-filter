# rapla-filter

An REST API designed to filter [RAPLA](https://rapla.org) schedules containing multiple courses by course.

## Requirements

Requirements can be found in the `requirements.txt` file.

## Installation

The preferred way of installing rapla-filter is using the docker image

An alternate image including the `swagger-ui` is available under the `dev` tag.  
This version also does not use `gunicorn` and should therefore not be used in production environments.

Example `docker-compose.yml`:  

```yaml

version: "2"
services:
    rapla-filter:
        image: baswag/rapla-filter
        container_name: rapla-filter
        environment:
            - TZ=Europe/Berlin
            - APP_RAPLA_URL=<MAIN_RAPLA_URL>
            - APP_FCM_KEY=<YOUR_FIREBASE_API_KEY>
        ports:
            - 5000:5000
        volumes:
            - rapla-filter-notifications:/app/notifications
        restart: unless-stopped
volumes:
    rapla-filter-notifications:
```

The `APP_RAPLA_URL` environment variable has to be in the format  
`http://hostname/rapla?page=ical&user={}&file={}`  
The Firebase API key can be obtained in the Firebase Console  

## Building

To build the development docker image simply run `docker build .`.  
To build the production docker image use the `--target prod` option when building

## Notifications

Notifications are handeled via a Firebase Cloud Messaging Service

## API Endpoints

If `connexion` is installed with the optional `swagger-ui` package the swagger UI will be served at `localhost:5000/api/ui`

## Common Parameters

- `uname` - The username of the RAPLA schedule creator
- `planname` - The name of the schedule in RAPLA
- `course` - The course the schedule should be filtered by

## /schedule/{uname}/{planname}/plain

This endpoint returns the unfiltered ICAL string from RAPLA  

## /schedule/{uname}/{planname}?course={course}

This endpoint returns the ICAL string from RAPLA filtered by course

## /schedule/{uname}/{planname}/notification?course={course}

This endpoint redirects the user to the [notify.run](https://notify.run) notification sign-up page for the specified plan filtered by course  

## /notification/subscribe?uname={uname}&planname={planname}&course={course}&token={token}

This endpoint adds or removes a FCM client identified by {token} from the notifications for a course

## /notification/status?uname={uname}&planname={planname}&course={course}&token={token}

This endpoint returns a boolean describing whether a FCM client identified by {token} is subscribed to the given notifications
