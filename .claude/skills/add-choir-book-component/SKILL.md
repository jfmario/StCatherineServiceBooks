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

- Design the component. It may involve an S3 Path to a PDF, incorporating an existing md file, or writing a new md file.

- Add the component after the indicated existing component. If an existing component is not given, add the new component to the end of the `Components` key.

Notes:

- You do not have access to the S3 bucket in this context. You can trust that the S3 paths given to you exist. If not, the build failure will make this clear to the user.

- Component md files live in directories under `components/`. 
