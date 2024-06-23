---
image: "image.jpg"
date: {{ .Date }}
slug: {{ now.Format "2006-01-02" }}-{{ .Name | urlize }}
type: "gallery"
title: "{{ replace .Name "-" " " | title }}"
draft: true
categories:
  - default
tags:
  - default
---

