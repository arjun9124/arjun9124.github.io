---
title: "Make Youtube Distraction Free"
date: 2023-06-24T14:05:25+05:30
slug: 2023-06-24-make-youtube-distraction-free
type: posts
draft: false
categories:
  - default
tags:
  - default
---

Over the years, it has become increasingly hard to focus on the web. With websites and serveices now being designed to make you shuttle from one red dot to another, it has become necessary for us users to preserve our integrities as users and to not become consumers. 
This article will guide you to removing all sorts of distractions from YouTube, a popular video sharing website which houses a library of videos ranging from casual entertainment to perhaps the best lectures in calculus. For the ones who use this as a tool to study, it is not possible to use the platform while keeping together their focus on what's important. 

By following these steps, you can:
* remove all advertisements
* remove all comments
* remove all recommendations
* remove all clickbait
from YouTube. 

## On Phone

On android you can use an application called New Pipe, it does whatever I have described above. 
Get it from https://newpipe.net/ 

## For web browsers:

### Install U-block Origin 
https://ublockorigin.com/

U-Block origin is not only an ad blocker, but a wide range content blocker and can be used to remove a variety of elements from a webpage. 

This shall be used not only to remove advertisements, but also recommendations, trending pages and other elements of this platform designed to distract you.

Add this to your U-Block filters: 
``` 
www.youtube.com###sections
www.youtube.com###ticker > .ytd-masthead.style-scope


!  block recommendations at the end of the video
! do not forget to disable autoplay at the end of the video. To do that: turn off ublock for a sec and then disable autoplay -> then turn it on again

www.youtube.com##.ytp-ce-element
www.youtube.com##.ytp-show-tiles.videowall-endscreen.ytp-player-content.html5-endscreen

! block home screen stuff
www.youtube.com##ytd-browse.ytd-page-manager[page-subtype="home"]

! block mobile home screen stuff
m.youtube.com##div[tab-identifier="FEwhat_to_watch"]

! block recommendations and comments on mobile
m.youtube.com##ytm-item-section-renderer.scwnr-content:nth-of-type(2)
m.youtube.com##ytm-comment-section-renderer.scwnr-content

! The recommendations that are at the end of a video https://www.youtube.com
www.youtube.com##ytd-watch-next-secondary-results-renderer.ytd-watch-flexy.style-scope > .ytd-watch-next-secondary-results-renderer.style-scope
www.youtube.com##ytd-shorts.ytd-page-manager.style-scope  
```

### Install Sponsorblock 

https://sponsor.ajay.app/

A community project where you can contribute yourself, sponsor block automatically skips the non essential parts of a video. Sponsor messages, subscription reminders, filler tangents, recaps etc. 

### Install De-Arrow

https://dearrow.ajay.app/

Another tool from the developer of Sponsorblock, it removes the thumbnail video and replaces it with a random screenshot from the video. Practically rendering clickbait useless.

### Install YouTube Shorts redirect

https://chrome.google.com/webstore/detail/redirect-shorts/

Why the short video format is bad -> https://cipirit.netlify.app/posts/short-video-format

The short video format is a closed , non consensual, algorithm based, freedom infringing video format. 
Youtube allows you to view shorts as regular videos as well, which prevents you from going into compulsive scrolling loops. 

### Install YouTube Transcript Generator (Optional)

https://chrome.google.com/webstore/detail/youtube-transcript-extrac/

Text is a better medium than video or audio. For video essays, or other media where the video does not play an important role its a viable option to read the transcript than to watch the video. 



