function is_letter(ch) {
    return (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z');
}

function is_digit(ch) {
    return ch >= '0' && ch <= '9';
}

function tokenizeTeX(tex) {
    let token = 0;
    let k = 0;
    const result = [];

    while (k < tex.length) {
        let ch = tex[k];
        if (is_digit(ch)) {
            const start = k++;
            while (k < tex.length && is_digit(tex[k]))
                k++;
            result.push({token: 'number', value: tex.substring(start, k)});
        } else if (is_letter(ch)) {
            const start = k++;
            while (k < tex.length && is_letter(tex[k]))
                k++;
            result.push({token: 'text', value: tex.substring(start, k)});
        } else if (ch === ' ') {
            const start = k++;
            while (k < tex.length && tex[k] === ' ')
                k++;
            result.push({token: ' ', value: k - start});
        } else if (ch === '{' || ch === '}' || ch === '$') {
            result.push({token: ch});
            k++;
        } else if (ch === '\\' && k + 1 < tex.length) {
            ch = tex[++k];
            if ('&%$#_{}~^\\'.indexOf(ch) >= 0) {
                result.push({token: 'symbol', value: '\\' + ch});
                k++;
            } else if (is_letter(ch)) {
                const start = k++;
                while (k < tex.length && is_letter(tex[k]))
                    k++;
                result.push({token: 'cmd', value: tex.substring(start-1, k)});
            } else {
                result.push({token: 'symbol', value: '\\'});
            }
        } else {
            result.push({token: 'symbol', value: ch});
            k++;
        }
    }

    return result;
}

function SyntaxError() {}

function normalizeText(strs, tokens, k) {
    let braces = 0;

    while (k < tokens.length) {
        if (tokens[k].token === ' ') {
            strs.push(' ');
            k++;
        } else if (tokens[k].token === '{') {
            braces++;
            strs.push('{');
            k++;
        } else if (tokens[k].token === '}') {
            braces--;
            strs.push('}');
            k++;
            if (braces === 0)
                return k;
        } else if (tokens[k].token === '$') {
            if (braces === 0)
                throw new SyntaxError();
            strs.push('$');
            k = normalizeMath(strs, tokens, k+1, true);
        } else {
            strs.push(tokens[k].value);
            k++;
            if (braces === 0)
                return k;
        }
    }

    throw new SyntaxError();
}

function normalizeMath(strs, tokens, k, dollarBegin) {
    let braces = 0;
    while (k < tokens.length) {
        if (tokens[k].token === ' ') {
            if (k > 0 && tokens[k-1].token === 'cmd' && k+1 < tokens.length && tokens[k+1].token === 'text')
                strs.push(' ');
            k++;
        } else if (tokens[k].token === '{') {
            braces++;
            strs.push('{');
            k++;
        } else if (tokens[k].token === '}') {
            if (braces === 0)
                throw new SyntaxError();
            braces--;
            strs.push('}');
            k++;
        } else if (tokens[k].token === '$') {
            if (braces != 0 || !dollarBegin)
                throw new SyntaxError();
            strs.push('$');
            return k+1;
        } else if (tokens[k].token === 'cmd' && tokens[k].value === '\\text') {
            strs.push('\\text');
            k++;
            if (k < tokens.length && tokens[k].token === ' ') {
                k++;
                if (k < tokens.length && tokens[k].token === 'text')
                    strs.push(' ');
            }
            k = normalizeText(strs, tokens, k);
        } else {
            strs.push(tokens[k].value);
            k++;
        }
    }
    if (dollarBegin)
        throw new SyntaxError();
}

function normalizeTeX(tex) {
    const tokens = tokenizeTeX(tex);
    const strs = [];

    try {
        normalizeMath(strs, tokens, 0, false);
    } catch (e) {
        if (e instanceof SyntaxError) {
            console.log('error');
            return tex;
        }
        throw e;
    }

    return strs.join('');
}

//const st = 'p \\text{ prime   $ x^ \\text 2$}';
//const st = '\\text {$1$}';
//const st = '\\text a b';
const st = '2^x y';
//const st = '\\pi   {x ';

console.log(tokenizeTeX(st));
console.log(normalizeTeX(st));
