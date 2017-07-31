// Adapted from https://github.com/douglascrockford/JSON-js/blob/master/json2.js

const rx_one = /^[\],:{}\s]*$/;
const rx_two = /\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g;
const rx_three = /"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g;
const rx_unquoted_keys = /[,{]\s*[$_a-zA-Z][$_a-zA-Z0-9]*\s*:/g;
const rx_four = /(?:^|:|,)(?:\s*\[)+/g;
const rx_dangerous = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g;

export default function (text) {

    // Parsing happens in four stages. In the first stage, we replace certain
    // Unicode characters with escape sequences. JavaScript handles many characters
    // incorrectly, either silently deleting them, or treating them as line endings.

    text = String(text);
    rx_dangerous.lastIndex = 0;
    if (rx_dangerous.test(text)) {
        text = text.replace(rx_dangerous, function (a) {
            return "\\u" +
                    ("0000" + a.charCodeAt(0).toString(16)).slice(-4);
        });
    }

    // In the second stage, we run the text against regular expressions that look
    // for non-JSON patterns. We are especially concerned with "()" and "new"
    // because they can cause invocation, and "=" because it can cause mutation.
    // But just to be safe, we want to reject all unexpected forms.

    // We split the second stage into 4 regexp operations in order to work around
    // crippling inefficiencies in IE's and Safari's regexp engines. First we
    // replace the JSON backslash pairs with "@" (a non-JSON character). Second, we
    // replace all simple value tokens with "]" characters. Third, we delete all
    // open brackets that follow a colon or comma or that begin the text. Finally,
    // we look to see that the remaining characters are only whitespace or "]" or
    // "," or ":" or "{" or "}". If that is so, then the text is safe for eval.

    if (
        rx_one.test(
            text
                .replace(rx_two, "@")
                .replace(rx_three, "]")
                .replace(rx_unquoted_keys, "]:")
                .replace(rx_four, "")
        )
    ) {

    // In the third stage we use the eval function to compile the text into a
    // JavaScript structure. The "{" operator is subject to a syntactic ambiguity
    // in JavaScript: it can begin a block or an object literal. We wrap the text
    // in parens to eliminate the ambiguity.

        return eval("(" + text + ")");

    }

    // If the text is not JSON parseable, then a SyntaxError is thrown.

    throw new SyntaxError("json_parse_relax_keys");
};
