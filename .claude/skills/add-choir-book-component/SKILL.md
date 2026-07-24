---
name: add-choir-book-component
description: Add a component to a choir book project.
disable-model-invocation: true
---

The user will provide:

- The service name
- The component name
- A description of the component
- (Optional) The existing component after which the new component should be placed
- (Optional) An example

The description might include an S3 path.

Instructions:

- If the service book does not exist in `projects/choir-books/`, create it according to the below starter.

<choir-book-project>
```yaml
Name: <serviceName/>
Subtitle: St Catherine Orthodox Church

Description: <description/>

Filename: <fileName/>

# Instructions: TODO

Components:
```
</choir-book-project>

- 
