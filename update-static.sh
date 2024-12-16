#!/bin/bash

cat <<EOF > /dev/null
    <script type="importmap" class="addedbyvrunner">
      {
        "imports": {
          "#vue": "/.runner/vue.esm-browser.prod.js", "DOWNLOAD:https://unpkg.com/vue@3/dist/vue.esm-browser.prod.js":"",
          ...
EOF


function get() {
    # key is e.g. #vue
    local key=$1
    local pathurl=$(cat vuejspython/index.html | grep "\"$key\": " | sed -e 's@.*: "/.runner/\(.*\)", "DOWNLOAD:\(.*\)":"".*@\1|||\2@g')
    local path=${pathurl%|||*}
    local url=${pathurl#*|||}
    echo -e "\n\n# \"$url\" ⇒ \"$path\"\n"
    wget "$url" -O "vuejspython/$path"
}


get '#vue' https://unpkg.com/vue@3/dist/vue.esm-browser.prod.js
get '#sfc' https://cdn.jsdelivr.net/npm/vue3-sfc-loader/dist/vue3-sfc-loader.esm.js