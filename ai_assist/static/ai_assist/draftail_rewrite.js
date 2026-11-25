// Draftail control: rewrite the selected blocks in the OpenStax voice.
//
// Wagtail's own converter does the HTML round trip server-side, so this only
// ever moves ContentState across the wire — nothing here needs to know which
// tags the field allows.
(() => {
  const configElement = document.getElementById('ai-assist-config');
  if (!configElement || !window.draftail || !window.DraftJS) {
    return;
  }
  const config = JSON.parse(configElement.textContent);
  const { ContentState, EditorState, Modifier, SelectionState, convertFromRaw, convertToRaw } =
    window.DraftJS;

  const selectedBlocks = (content, selection) => {
    if (selection.isCollapsed()) {
      return content.getBlocksAsArray();
    }
    const startKey = selection.getStartKey();
    const endKey = selection.getEndKey();
    return content
      .getBlockMap()
      .skipUntil((_, key) => key === startKey)
      .takeUntil((_, key) => key === endKey)
      .toArray()
      .concat([content.getBlockForKey(endKey)]);
  };

  const wholeBlocks = (blocks) => {
    const first = blocks[0];
    const last = blocks[blocks.length - 1];
    return SelectionState.createEmpty(first.getKey()).merge({
      anchorKey: first.getKey(),
      anchorOffset: 0,
      focusKey: last.getKey(),
      focusOffset: last.getLength(),
      isBackward: false,
    });
  };

  const editorInput = (element) => {
    const wrapper = element && element.closest('[data-draftail-editor-wrapper]');
    // Wagtail appends the wrapper next to the hidden input it initialised from.
    return wrapper && wrapper.parentNode.querySelector('[data-draftail-input]');
  };

  const editorOptions = (input) => {
    try {
      return JSON.parse(input.getAttribute('data-w-init-detail-value') || '{}');
    } catch (error) {
      return {};
    }
  };

  const fieldLabel = (input) => {
    const field = input.closest('[data-field-wrapper], .w-field__wrapper');
    const label = field && field.querySelector('label');
    return label ? label.textContent.trim() : '';
  };

  const currentPageId = () => {
    const match = window.location.pathname.match(/\/pages\/(\d+)\/edit/);
    return match ? match[1] : null;
  };

  const requestRewrite = async (body, signal) => {
    const response = await fetch(config.rewriteUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        [window.wagtailConfig.CSRF_HEADER_NAME]: window.wagtailConfig.CSRF_TOKEN,
      },
      body: JSON.stringify(body),
      signal,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'The rewrite failed.');
    }
    return data.contentstate;
  };

  const OpenStaxVoiceControl = ({ getEditorState, onChange }) => {
    const [busy, setBusy] = window.React.useState(false);
    const [error, setError] = window.React.useState(null);
    const anchor = window.React.useRef();

    const rewrite = async () => {
      const input = editorInput(anchor.current);
      if (!input || busy) {
        return;
      }
      const editorState = getEditorState();
      const content = editorState.getCurrentContent();
      const blocks = selectedBlocks(content, editorState.getSelection());
      const fragment = ContentState.createFromBlockArray(blocks, content.getEntityMap());

      setError(null);
      setBusy(true);
      try {
        const rewritten = await requestRewrite({
          contentstate: convertToRaw(fragment),
          editorOptions: editorOptions(input),
          pageId: currentPageId(),
          fieldLabel: fieldLabel(input),
        });
        const replacement = Modifier.replaceWithFragment(
          content,
          wholeBlocks(blocks),
          convertFromRaw(rewritten).getBlockMap(),
        );
        onChange(EditorState.push(editorState, replacement, 'insert-fragment'));
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setBusy(false);
      }
    };

    return window.React.createElement(
      window.React.Fragment,
      null,
      window.React.createElement(window.Draftail.ToolbarButton, {
        name: 'OPENSTAX_VOICE',
        title: busy ? 'Rewriting…' : 'Rewrite in OpenStax voice',
        icon: window.React.createElement(window.Draftail.Icon, {
          icon: busy ? '#icon-spinner' : '#icon-wand',
        }),
        onClick: rewrite,
      }),
      window.React.createElement('span', { ref: anchor }),
      error
        ? window.React.createElement('span', { className: 'error-message' }, error)
        : null,
    );
  };

  window.draftail.registerPlugin(
    { type: 'openstax-voice', inline: OpenStaxVoiceControl },
    'controls',
  );
})();
