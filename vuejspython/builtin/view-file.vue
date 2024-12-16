<template>
    <add-in-head>
        <title>View File</title>
    </add-in-head>
    <div>
        <h1><pre>{{ file }}</pre></h1>
        <pre>{{ content }}</pre>
    </div>
</template>
<script setup>
import { ref } from '#vue';
const { args, fs } = window.VueRunner;

const file = args[0];
const content = ref('loading...');

(async () => {
    content.value = await fs.readFile(file);
})()
</script>
