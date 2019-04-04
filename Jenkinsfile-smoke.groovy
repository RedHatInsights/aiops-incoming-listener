/*
 * Requires: https://github.com/RedHatInsights/insights-pipeline-lib
 */

@Library("github.com/RedHatInsights/insights-pipeline-lib") _

// Smoke tests are run via a GitHub comment trigger
properties([
    pipelineTriggers([
        issueCommentTrigger('.*smoke test please.*'),
    ])
])

def comment = triggeredByComment()
echo "Triggered by comment: ${comment}"

if (comment) {
    runSmokeTest (
        ocDeployerBuilderPath: "aiops/aiops-incoming-listener",
        ocDeployerComponentPath: "aiops/aiops-incoming-listener",
        ocDeployerServiceSets: "aiops",
        pytestMarker: "aiops_smoke",
        iqePlugins: "iqe-aiops-plugin"
    )
}
