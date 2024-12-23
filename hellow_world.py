from hera.workflows import Steps, Workflow, WorkflowsService, script


@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="hello-world-",
    entrypoint="steps",
    namespace="kornerstone-ml",
    workflows_service=WorkflowsService(host="https://localhost:2746", verify_ssl=False),
) as w:
    with Steps(name="steps"):
        echo(arguments={"message": "Hello world!"})

w.create()
