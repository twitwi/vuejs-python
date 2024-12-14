<template>
    <add-in-head>
        <title>Exam Toggle</title>
    </add-in-head>
    <CSSRules/>
    <div class="tabs">
        <span v-for="f in args" @click="clickFile(f)" :class="{current: currentFile === f }">{{ f }}</span>
    </div>
    <h1>File {{ currentFile }} (commentPrefix is <pre>{{ commentPrefix }}</pre>)</h1>
    <table>
        <thead>
        <tr>
            <th v-for="s in shown" :title="info[s]">{{s}}</th>
        </tr>
        </thead>
        <tr v-for="d,dindex in data">
            <td v-for="s, index in shown" :class="'meta--'+s">
                <span v-if="d.special === 'separator'"></span>
                <input v-else-if="index === last || editAll" :id="index === last ? 'lastcb--'+dindex : ''" type="checkbox" :checked="d.appearsIn.includes(s)" @input="ev => toggle(d.appearsIn, s, ev.target.checked)" />
                <input v-else type="checkbox" :checked="d.appearsIn.includes(s)" disabled />
            </td>
            <td><label :for="'lastcb--'+dindex" :title="d.title"><pre>{{d.oneliner}}</pre></label></td>
        </tr>
    </table>
    <hr/>
    <h3>Would write <button @click="() => commit()">Do WRITE</button></h3>
    <div class="diff">
    DIFF:<br/>
    <span v-for="p in diff" :class="{ added: p.added, removed: p.removed}">{{ p.value }}</span>
    </div>
    <pre>
    RAW:
    {{ willWrite }}
    </pre>
    <hr/>
    <h3>Last Read</h3>
    <pre>
    {{ lastReadContent }}
    </pre>
</template>
<style>
.tabs {
    line-height: 2.1em;
}
.tabs > span {
    display: inline-block;
    border: 4px solid grey;
    background: #EEE;
    padding: 0 1em;
    margin: 0.2em 1em;
}
.tabs > span:not(.current):hover {
    border-color: blueviolet;
}
.tabs > span.current {
    border-color: black;
}
tr:first-of-type {
    border-top: 1px solid grey;
}
thead {
    position: sticky;
    top: 20px;
    background: white;
}
td pre {
    margin: 0;
    font-weight: bold;
}
th {
    font-size: .8em;
    height: 10px;
    max-width: 20px;
    transform: translate(9px, 0px) rotate(-45deg);
    white-space: nowrap;
    border-bottom: 1px solid grey;
    padding: 0;
}
label:hover {
    text-decoration: underline;
}
h1 pre {
    display: inline-block;
    border: 1px solid grey;
}
.diff {
    white-space: pre;
    font-family: monospace;
    position: fixed;
    top: 10em; right: 0; bottom: 0;
    border: 1px solid black;
    font-size: .8rem;
    max-width: 50vw;
    overflow: scroll;
    background: #fef3c79f;
    padding: 2em;
}
.diff:hover {
    background: #fef8dc;
}
.diff .added {
    background-color: #a7f3d0;
    color: #064e3b;
}
.diff .removed {
    background-color: #7f1d1d;
    color: #fecaca;
}
</style>
<script type="module">
const { args, fs, onHash, setHash } = window.VueRunner;
import { h } from 'vue'
const Diff = require('.assets/diff.min.js')

function JSONparse(txt) {
    try {
        return JSON.parse(txt);
    } catch(e) {
        console.log("EXCEPTION IN JSON.parse", txt, e)
        throw e;
    }
}

export default {
    props: {
        args: { default: args },
    },
    components: {
        CSSRules: {
            render() {
                return h('style', {innerHTML: this.$parent.style})
            }
        }
    },
    data: () => ({
        currentFile: '',
        editAll: false,
        commentPrefix: '%%% ',
        nocommentPrefix: ' ',
        shown: [],
        highlighted: {},
        info: {},
        data: [],
        lastReadContent: '',
        willWrite: '',
        diff: {},
    }),
    async mounted() {
        window.vm = this
        onHash(async (h) => {
            if (!h) {
                setHash(this.args[0])
            } else {
                await this.openFile(h)
            }
        });
    },
    computed: {
        last() {
            return this.shown.length - 1
        },
        style() {
            return Object.entries(this.highlighted).map(([k, v]) => `.meta--${k} { ${v} }`).join('\n\n')
        },
    },
    methods: {
        clickFile(f) {
            setHash(f)
        },
        async openFile(f) {
            this.currentFile = f
            this.diff = {}
            setHash(f)
            await this.reload()
        },
        async toggle(arr, txt, add) {
            const deleted = '::DELETED::'+txt
            const i = arr.indexOf(txt)
            const j = arr.indexOf(deleted)
            if (i > -1) {
                arr[i] = deleted
            } else if (j > -1) {
                arr[j] = txt
            } else {
                arr.push(txt)
            }
            this.dryRun()
        },
        async _parse_and_digest_config(diskLines, path) {
            for (const i in diskLines) {
                const l = diskLines[i]
                if (l.includes('META-PREFIXES:')) {
                    [this.commentPrefix, this.nocommentPrefix] = JSONparse(l.split(/META-PREFIXES:/, 2)[1])
                } else if (l.includes('META-SHOW:')) {
                    const [prefix, shown] = l.split(/META-SHOW:/, 2)
                    this.commentPrefix = prefix
                    this.shown = JSONparse(shown)
                } else if (l.includes('META-HIGHLIGHT:')) {
                    const [, highlight] = l.split(/META-HIGHLIGHT:/, 2)
                    this.highlighted = {...this.highlighted, ...JSONparse(highlight)}
                } else if (l.includes('META-INFO:')) {
                    const [k, v] = l.split(/META-INFO: */, 2)[1].split(/ *::: */)
                    this.info[k] = v
                } else if (l.includes('META-INCLUDE:')) {
                    const [k, v] = l.split(/META-INCLUDE: */, 2)
                    const includePath = [...path.split(/\//g).slice(0, -1), v].join('/')
                    console.log(`Including '${v}' as '${includePath}'`)
                    const includeLines = (await fs.readFile(includePath)).split(/\n/g);
                    await this._parse_and_digest_config(includeLines, includePath)
                }
            }
        },
        async _loadAndIterate(checkEquals, mode) {
            const isRead = mode !== 'WRITE'
            if (isRead) {
                this.data = []
                this.commentPrefix = '%%% '
                this.nocommentPrefix = ' '
                this.shown = []
                this.highlighted = {}
                this.info = {}
                this.data = []
            }
            const path = this.currentFile
            const diskContent = await fs.readFile(path);
            if (checkEquals) {
                if (diskContent !== this.lastReadContent) {
                    console.log("Failed equality test", "DISK", diskContent, "LAST", this.lastReadContent)
                    return false
                }
            }
            let diskLines = diskContent.split(/\n/g)
            if (isRead) {
                this.lastReadContent = diskContent
                await this._parse_and_digest_config(diskLines, path)
            }
            let state = 'base'
            let mem = {}
            let i = 0
            let iData = 0
            while (i < diskLines.length) {
                let l = diskLines[i]
                if (state === 'base') {
                    if (l.includes('META:')) {
                        const [prefix, suffix] = l.split(/META:/, 2)
                        if (isRead) {
                            const appearsIn = JSONparse(suffix)
                            this.data.push({
                                l, prefix, suffix, appearsIn, oneliner: prefix, title: l,
                            })
                        } else {
                            const app = this.data[iData].appearsIn.filter(v => !v.startsWith('::DELETED::'))
                            const isPresent = this.data[iData].appearsIn.includes(this.shown.slice(-1)[0])
                            const P = isPresent ? this.nocommentPrefix : this.commentPrefix
                            const S = prefix.startsWith(this.commentPrefix) ? prefix.substring(this.commentPrefix.length) : prefix.startsWith(this.nocommentPrefix) ? prefix.substring(this.nocommentPrefix.length) : prefix
                            diskLines[i] = `${P}${S.trimLeft()}META: ${JSON.stringify(app, null, " ").replaceAll("\n", "").replaceAll('[ ', '[')}`
                            iData++
                        }
                    } else if (l.includes('METABEGIN:')) {
                        state = 'inblock'
                        const [prefix, suffix1] = l.split(/METABEGIN:/, 2)
                        const [desc, suffix] = suffix1.split(/ *::: */)
                        if (isRead) {
                            const appearsIn = JSONparse(suffix)
                            this.data.push({
                                l, prefix, suffix, appearsIn, oneliner: '(((block))) ' + desc, title: '', special: 'block'
                            })
                        } else {
                            const app = this.data[iData].appearsIn.filter(v => !v.startsWith('::DELETED::'))
                            mem.isPresent = this.data[iData].appearsIn.includes(this.shown.slice(-1)[0])
                            diskLines[i] = `${prefix}METABEGIN:${desc} ::: ${JSON.stringify(app, null, " ").replaceAll("\n", "").replaceAll('[ ', '[')}`
                            iData++
                        }
                    } else if (l.includes('METASEP')) {
                        const [prefix, suffix] = l.split(/METASEP/, 2)
                        if (isRead) {
                            this.data.push({
                                l, prefix, suffix, appearsIn: [], oneliner: '(((separator))) ' + suffix, title: l, special: 'separator'
                            })
                        } else {
                            iData++
                        }
                    }
                } else if (state === 'inblock') {
                    if (l.includes('METAEND')) {
                        state = 'base'
                    } else {
                        if (isRead) {
                            this.data.slice(-1)[0].title += '\n' + l
                        } else {
                            const { isPresent } = mem
                            const P = isPresent ? this.nocommentPrefix : this.commentPrefix
                            const S = l.startsWith(this.commentPrefix) ? l.substring(this.commentPrefix.length) : l.startsWith(this.nocommentPrefix) ? l.substring(this.nocommentPrefix.length) : l
                            diskLines[i] = `${P}${S}`
                        }
                    }
                }
                i++
            }
            if (!isRead) {
                this.willWrite = diskLines.join('\n')
                this.diff = Diff.diffChars(this.lastReadContent, this.willWrite)
            }
            return true
        },
        async reload() {
            this.lastReadContent = '(((reloading...)))'
            await this._loadAndIterate(false, 'READ')
            
        },
        async dryRun() {
            try {
                await this._loadAndIterate(true, 'WRITE')
            } catch {
                this.willWrite = '(((ERROR...)))'
                this.diff = {}
            }
        },
        async commit() {
            this.willWrite = '(((will write...)))'
            if (await this._loadAndIterate(true, 'WRITE')) {
                await fs.writeFile(this.currentFile, this.willWrite)
                await this.reload()
            }
        },
    },
}
</script>
