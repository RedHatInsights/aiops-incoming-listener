# AI-Ops incoming data listener

Kafka listener collecting messages containing data relevant to AI-Ops

## OpenShift Deployment

First upload and create all needed resourced from our template

```
❯ oc create -f aiops-incoming-listener-template.yaml
template.template.openshift.io "aiops-incoming-listener" created
```

Then create the application - this would create `Service`, `DeploymentConfig`, `BuildConfig` as well as `ImageStream`

```
❯ oc new-app --template aiops-incoming-listener
--> Deploying template "<PROJECT>/aiops-incoming-listener" to project <PROJECT>

--> Creating resources ...
    service "aiops-incoming-listener" created
    deploymentconfig "aiops-incoming-listener" created
    buildconfig "aiops-incoming-listener" created
    imagestream "aiops-incoming-listener" created
--> Success
    Build scheduled, use 'oc logs -f bc/aiops-incoming-listener' to track its progress.
    Application is not exposed. You can expose services to the outside world by executing one or more of the commands below:
     'oc expose svc/aiops-incoming-li
```

The previous command already triggered a build and deployment of the application.

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
