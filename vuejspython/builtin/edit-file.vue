<template>
    <add-in-head>
        <title>Edit File</title>
    </add-in-head>
    <div>
        <h1><pre>{{ file }}</pre></h1>
        <div>
            <button @click="refresh()">reload</button>
            <button @click="save()" :disabled="content == lastContent">save</button>
        </div>
        <textarea v-model="content"></textarea>
    </div>
</template>
<style>
button {
    margin: 1em;
}
textarea {
    margin: 1em -0.2em;
    width: 100%;
    height: 80vh;
}
</style>
<script setup>
import { ref } from 'vue';
const { args, fs } = window.VueRunner;

const file = args[0];
const lastContent = ref('loading...');
const content = ref(lastContent.value);

async function refresh() {
    content.value = await fs.readFile(file)
    lastContent.value = content.value;
}

async function save() {
    await fs.writeFile(file, content.value);
    await refresh();
    /*
    fetch(`/.file/${file}`, {
        method: 'POST',
        body: content.value,
    }).then(()=> {
        refresh();
    });*/
}

refresh();
</script>
