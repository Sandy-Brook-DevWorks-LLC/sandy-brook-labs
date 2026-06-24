(function () {
    function escapeHtml(value) {
        return value
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
    }

    function highlightLine(line) {
        var placeholders = []

        function placeholderToken(index) {
            var letters = ''
            do {
                letters = String.fromCharCode(97 + (index % 26)) + letters
                index = Math.floor(index / 26) - 1
            } while (index >= 0)

            return '\u0000hold' + letters + '\u0000'
        }

        function hold(pattern, className) {
            line = line.replace(pattern, function (match) {
                var token = placeholderToken(placeholders.length)
                placeholders.push('<span class="' + className + '">' + match + '</span>')
                return token
            })
        }

        hold(/\/\/.*/g, 'cm')
        hold(/"([^"\\]|\\.)*"/g, 'str')
        hold(/\b\d+(\.\d+)?\b/g, 'num')

        line = line
            .replace(/\b(public|private|protected|internal|static|sealed|class|interface|record|enum|var|new|return|async|await|using|namespace|if|else|for|foreach|while|switch|case|try|catch|finally|throw|in|not|null|true|false)\b/g, '<span class="kw">$1</span>')
            .replace(/\b(string|int|long|double|float|bool|Guid|Task|IReadOnlyList|IReadOnlyCollection|CancellationToken|HttpRequest|RagDbContext|IObjectStorage|IOptions|RagOptions|DocumentRecord|DocumentStatus|AskRequest|IChatAnswerService|AskResponse|CitationDto|Dictionary|object)\b/g, '<span class="tp">$1</span>')
            .replace(/\b([A-Za-z_][A-Za-z0-9_]*)\s*(?=\()/g, '<span class="fn">$1</span>')
            .replace(/\b(Upload|Extract|Chunk|Embed|Retrieve|Answer|Pending|Processing|Indexed|Failed)\b/g, '<span class="pk">$1</span>')

        placeholders.forEach(function (value, index) {
            line = line.replace(placeholderToken(index), value)
        })
        return line
    }

    function highlightBlock(block) {
        var text = block.textContent
        block.innerHTML = escapeHtml(text).split('\n').map(highlightLine).join('\n')
        block.classList.add('is-highlighted')
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.rag-main pre code').forEach(highlightBlock)
    })
})()
