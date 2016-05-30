import marked from 'marked';

marked.setOptions({
  gfm: false,
  pedantic: false,
  sanitize: true,
});

export default function markdownify(text) {
    return Promise.resolve(marked(text));
}
