---
image: "image.jpg"
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
slug: {{ now.Format "2006-01-02" }}-{{ .Name | urlize }}
type: gallery
draft: true
categories:
  - default
tags:
  - default
---


