# CHAMP 

This repository includes the code of CHAMP, an effective tool for annotating and consolidating a hierarchy of clusters. 

## Annotation:

![Alt text](src/assets/annotation.png)


## Consolidation

<p align="center">
  <img src="src/assets/cons_coref.png" width="49%" />
  <img src="src/assets/cons_hierarchy.png" width="49%" />
</p>


For a full walkthrough of CHAMP's features, check out our system demonstration video on [youtube](https://youtu.be/1n4d6RyAP0M|).


## How to use CHAMP?

### 1.  Annotation portal 

The easiest way to use CHAMP is with the annotation [portal](https://cattana.pythonanywhere.com/), which allows you to update a JSON configuration file for annotation or consolidation, perform the task and download it upon completion. 

### 2. CDN 

Load `CHAMP` using CDN and embed the app as a WebComponent

```html
<script src="https://unpkg.com/vue"></script>
<script src="https://github.com/ariecattan/champ/releases/download/1.0.0/champ-app.min.js"></script>

<link href="https://fonts.googleapis.com/css?family=Roboto:100,300,400,500,700,900" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/@mdi/font@5.x/css/materialdesignicons.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/vuetify@2.x/dist/vuetify.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css?family=Material+Icons" rel="stylesheet">
```


```html
<champ-app json="{html escaped json config}" ></champ-app>
```

Results can be then extracted as follows:

```javascript
let champ = document.getElementsByTagName("champ-app")[0].vueComponent;
let results = {tokens:champ.tokens, mentions:champ.mentions}
JSON.stringify(results);
```

### 3. Install CHAMP locally

Clone this repo to your local machine 

```shell 
$ git clone https://github.com/ariecattan/champ.git
```

Then run the following npm commands to install and run the tool locally.
```shell
$ npm install
$ npm run --serve 
```


## Configurate champ

You can find example of input JSON files for each model in `src/examples`.

See below the important parameters in the JSON config file:
* `mode`: (onboarding, annotation, reviewer)
* `hierarchy`: (true or false) whether to allow or not annotation of hierarchy between clusters
* `tokens`: list of flatten tokens from all documents, each token needs to include {`i`: incremental index, `document`: doc_id of the document, `text`} and optionally `paragraph` 
* `mentions`: list of candidate mentions to annotate, each mention needs to include {`start`, `end`}. In addition, in the onboarding and reviewer mode, you also need to add a `clustId` field for each mention, which is an array of cluster IDs. The format of each cluster ID is "start-end" of the first mention in the cluster. For the annotation mode, only the first mention needs to have a `clustId`. 


Configurable options:
* `local`: True of False, whether to add a button for downloading the annotation at the end of the annotation

The hierarchy of clusters is built using simple drag-and-drop operations. 

Anntotators may also add notes for each node.

![Hypernym](src/assets/hypernym.gif)

Please refer to our [website](https://scico.apps.allenai.org/tool) for more details on the tool functionaly. 


---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**


## Citation 

