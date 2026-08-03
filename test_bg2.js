const fs = require('fs');
const data = JSON.parse(fs.readFileSync('debug_bg_data.json', 'utf-8'));

let codeToParent = {};
let hasChildren = {};
let allCodes = data.accounts.map(a => a.code);
for (let i = 0; i < allCodes.length; i++) {
    let code = allCodes[i];
    let parent = null;
    for (let j = i - 1; j >= 0; j--) {
        if (code.startsWith(allCodes[j])) {
            parent = allCodes[j];
            hasChildren[parent] = true;
            break;
        }
    }
    codeToParent[code] = parent;
}

let html = '';
let totActivo = null;
let totPasivo = null;
let totPatrimonio = null;
let totPasPat = { base: 0, m1_12: new Array(12).fill(0), y1: 0, y2: 0, y3: 0 };
let lastGroup = null;

try {
    data.accounts.forEach(acc => {
        let currentGroup = acc.code.charAt(0);
        lastGroup = currentGroup;
        
        let level = acc.code.length;
        let pad = (level - 1) * 1.5;
        if (level === 1) pad = 0;
        if (pad > 10) pad = 10;
        
        let parentCode = codeToParent[acc.code];
        
        let isAllZeros = acc.base === 0 && acc.y1 === 0 && acc.y2 === 0 && acc.y3 === 0;
        if (isAllZeros) {
            let mZero = true;
            for (let k = 0; k < 12; k++) {
                if (acc.m1_12[k] !== 0) { mZero = false; break; }
            }
        }
        
        if (acc.code === '1') totActivo = acc;
        if (acc.code === '2') totPasivo = acc;
        if (acc.code === '3') totPatrimonio = acc;
        
        if (acc.code === '2' || acc.code === '3') {
            totPasPat.base += acc.base;
            for(let i=0; i<12; i++) totPasPat.m1_12[i] += acc.m1_12[i];
            totPasPat.y1 += acc.y1; totPasPat.y2 += acc.y2; totPasPat.y3 += acc.y3;
        }
    });
    console.log('Success!');
} catch (e) {
    console.error('ERROR during forEach:', e);
}
