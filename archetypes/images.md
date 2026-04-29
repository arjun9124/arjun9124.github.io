\---

title: "{{ replace .Name "-" " " | title }}"

date: {{ .Date }}

slug: {{ now.Format "2006-01-02" }}-{{ .Name | urlize }}

type: posts

draft: true

description: 

categories:

&#x20; - default

tags:

&#x20; - default

\---

