<template>
    <add-in-head>
        <title>video serve</title>
        <link
        rel="icon"
        href="data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2016%2016'%3E%3Ctext%20style='filter:hue-rotate(-90deg)'%20x='0'%20y='14'%3E📺%3C/text%3E%3C/svg%3E"
        type="image/svg+xml"
      />
    </add-in-head>
    <div id="list" :class="{hidden: loading, force: !video}">
        <ul>
            <li v-for="f in files" :key="f" @click="play(f)">
                {{ f }}
            </li>
        </ul>
    </div>
    <div id="player">
        <video :src="video" controls ref="videoElement">
            <track :src="(video??'').replace(/[.][^.]*$/g, '.vtt')" kind="subtitles" srclang="en" label="English" default />
        </video>
    </div>
</template>

<script setup lang="ts">
import { ref } from "#vue";

const { fs, onHash, setHash } = window.VueRunner;

const loading = ref(false)
const video = ref('')
const videoElement = ref(null)
const files = ref([] as string[])

setInterval(()=> {
    if (videoElement.value) {
        const t = videoElement.value.currentTime
        if (t > 10) {
            localStorage.setItem('TIME:'+video.value, t)
        }
    }
}, 5000)

function play(f: string, t?: number) {
    video.value = f
    setHash(f)
    loading.value = true
    setTimeout(()=> {
        loading.value = false
        if (videoElement.value) {
            videoElement.value.currentTime = t ?? 0
            videoElement.value.play()
        }
    }, 10)
}

onHash(function (f) {
    const t = localStorage.getItem('TIME:' + f)
    if (t) {
        setTimeout(() => {
            if (confirm('Restart from minute ' + parseInt(parseFloat(t)/60) + '?')) {
                play(f, parseFloat(t))
            }
        }, 10)
    } else {
        play(f)
    }
})

async function start() {
    files.value = (await fs.listFiles()).files.filter(f => !f.startsWith('.'))
}
start()
</script>

<style>
body, html {
  padding: 0;
  margin: 0;
}
#player {
  background-color: #111;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  video {
      max-height: 100%;
  }
}
#list {
    padding: 1em;
    position: fixed;
    color: white;
    background: #222A;
    height: 90vh;
    transition: 1s all;
    width: 40vw;
    max-height: 100vh;
    overflow: scroll;
    font-size: 25px;
    line-height: 1.85;
    &:not(:hover):not(.force), &.hidden {
        opacity: 0;
        width: 0px;
    }
}
</style>
