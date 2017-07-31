export function normalizeTeX(tex) {
   return tex.trim().replace(/\s+/g, ' ')
}

export function TeX_brace_balance(tex) {
    let balance = 0;

    for (let k = 0; k < tex.length; k++) {
        const ch = tex[k];
        if (ch === '{') {
            balance++;
        } else if (ch === '}') {
            if (balance === 0)
                return -1e8;
            balance--;
        } else if (ch === '\\') {
            k++;
        }
    }

    return balance;
}