<template>
    <add-in-head>
        <title>Create Demo Files</title>
    </add-in-head>
    <div>
        Status: {{ status }}.
        <br/>
        Files:
        <ul>
            <li v-for="f in files" @click="currentFile = f" :class="{current: currentFile == f}">{{ f }}</li>
        </ul>
        <button @click="clearDemoFiles()">Clear Demo Files</button>
        <button @click="clearDemoFiles(false)">🐇</button>
        <br/>
        <button @click="createDemoFiles()">Re-Create Demo Files</button>
        <pre>{{ currentFileContent }}</pre>
    </div>
</template>
<style>
.current { font-weight: bold; }
</style>
<script setup>
import { ref, watch } from '#vue'; // embedded vue
const { fs } = window.VueRunner;

const currentFile = ref('');
const currentFileContent = ref('');
watch(currentFile, async (f) => {
    if (!f) {
        currentFileContent.value = '';
        return;
    }
    currentFileContent.value = 'loading...';
    currentFileContent.value = await fs.readFile(f);
});
const status = ref('init...');

async function createDemoFiles() {
    await updateFiles();
    currentFile.value = '';
    status.value = 'creating (slowly)...';
    const demoFiles = {
        'demo/file1.txt': 'This is the first file\nEnjoy vjspy!\n',
        'demo/file2.txt': 'This is the second of the files\n',
        'demo/file3.txt': 'This is finally the third file.\nThe best of all!\n',
        'demo/exam/minimalish.tex': `
%META-SHOW: ["sess1", "sess2", "sess3"]
%META-PREFIXES: ["%", " "]

%\\question{What is your favorite color?} %META: ["sess1", "sess2"]\n
 \\question{What is the airspeed velocity of an unladen swallow?} %META: ["test", "sess1", "sess3"]\n
\\question{How do you know so much about swallows?} %META: ["sess3"]\n
%METASEP: a separator here\n
%\\question{What is the color of the sky?} %META: []\n`,
/////
        'demo/exam/main.tex': `
% This is the main source file, with some config shared by all files it could include.\n
% In practice this file is META-INCLUDED by the other files.\n\n
%META-INFO: sess1 ::: The first session with these questions.\n
%META-INFO: sess3 ::: The third session with these questions.\n
%META-HIGHLIGHT: {"sess1": "background: lightred", "sess2": "background: orange", "sess2 :not(:checked)": "opacity: 0.2" }\n\n
%META-SHOW: ["sess1", "sess2", "sess3"]\n\n
This can contain toggles too.\n
\n
%\\question{What is your favorite color?} %META: ["sess1", "sess2"]\n
 \\question{What is the airspeed velocity of an unladen swallow?} %META: ["test", "sess1", "sess3"]\n
\\question{How do you know so much about swallows?} %META: ["sess3"]\n
%METASEP: a separator here\n
%\\question{What is the color of the sky?} %META: []\n\n
Commenting all lines in a block is also supported.\n
% METABEGIN: groupall ::: ["sess1", "sess2"]\n
%Bla bla bla\n
%Blo blo blob\n
% METAEND\n\n
`,
/////
        'demo/exam/secondary.tex': `
%META-INCLUDE: main.tex
\n
%\\question{What is your favorite color?} %META: ["sess1", "sess2"]\n
 \\question{What is the airspeed velocity of an unladen swallow?} %META: ["test", "sess1", "sess3"]\n
\\question{How do you know so much about swallows?} %META: ["sess3"]\n
%METASEP: a separator here\n
%\\question{What is the color of the sky?} %META: []\n`,
/////
    };

    for (const [path, content] of Object.entries(demoFiles)) {
        await fs.writeFile(path, content);
        await updateFiles();
    }
    status.value = 'created';
}

async function clearDemoFiles(updateALot = true) {
    if (updateALot) await updateFiles();
    status.value = `clearing (slowly = ${updateALot})...`;
    for (const f of files.value) {
        await fs.deleteFile(f);
        if (updateALot) await updateFiles();
    }
    await updateFiles();
    status.value = 'cleared';
}

const files = ref([]);
async function updateFiles() {
    files.value = (await fs.listFiles()).files.filter(f => f.startsWith('demo/') && !f.endsWith('/')).sort();
}

createDemoFiles();
</script>
