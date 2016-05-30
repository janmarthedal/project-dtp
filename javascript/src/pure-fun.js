export function object_to_array(obj) {
    const result = [];
    for (const key in obj)
        result.push([key, obj[key]]);
    return result;
}

export function array_to_object(list) {
    const result = {};
    list.forEach(item => {
        result[item[0]] = item[1];
    });
    return result;
}

export function normalizeTeX(tex) {
   return tex.trim().replace(/(\\[a-zA-Z]+) +([a-zA-Z])/g , '$1{\\\\}$2').replace(/ +/g, '').replace(/\{\\\\\}/g, ' ')
}
