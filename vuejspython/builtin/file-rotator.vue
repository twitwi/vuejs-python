<template>
    <add-in-head>
        <title>Rotate Files</title>
    </add-in-head>
    <div>
        <h1>Roate <pre>{{ files.length }} files</pre></h1>
        <div class="main">
            <div v-for="f in files" :class="{ wip: !fileContent[f] }">
                <h5>{{ f }}</h5>
                <pre>{{ fileContent[f] }}</pre>
            </div>
        </div>
        <button @click="rotate()">Rotate</button>
    </div>
</template>
<script setup>
import { ref, computed } from 'vue';
const { args, fs } = window.VueRunner;

const files = args;
const fileContent = ref({});

async function refresh() {
    const newFileContent = {};
    for (const f of files) {
        newFileContent[f] = await fs.readFile(f);
    }
    fileContent.value = newFileContent;
}
async function rotate() {
    await fetch('/.rotate');
    await refresh();
}
refresh();
</script>
<script lang="python">

@app.get("/.rotate")
def do_rotate():
    import os
    import sys
    import shutil
    import tempfile
    files = sys.argv[1:]

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    shutil.copyfile(files[0], temp_file.name)
    for i in range(len(files) - 1):
        shutil.copyfile(files[i + 1], files[i])
    shutil.copyfile(temp_file.name, files[-1])
    os.remove(temp_file.name)

</script>

