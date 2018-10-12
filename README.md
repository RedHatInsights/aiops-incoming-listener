# AI-Ops incoming data listener

Kafka listener collecting messages containing data relevant to AI-Ops

## OpenShift Deployment

Please consult [`aiops-deploy` repository](https://github.com/tumido/aiops-deploy) for deployment scheme.

# Local build

If you would like to deploy the clustering service locally, you can build the container using [S2I](https://github.com/openshift/source-to-image)

```
❯ s2i build -c . centos/python-36-centos7 aiops-incoming-listener
```

For convenience you can store your desired environment variables in a separate file

```
❯ cat << EOT >> env.list
KAFKA_SERVER=<HOSTNAME:PORT>
TOPIC=<SUBSCRIBED_TOPIC>
EOT
```

And then run it as a Docker container

```
❯ docker run --env-file env.list -it aiops-incoming-listener
```

# Related projects

- [Message bus for Insights platform](https://github.com/RedHatInsights/platform-mq)
- [AI service](https://github.com/RedHatInsights/aicoe-insights-clustering)
