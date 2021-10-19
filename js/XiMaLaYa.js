/**
 * Created by newer on 2021/10/19.
 */
Ot = require('crypto-js');

u=Ot.AES.decrypt({
       ciphertext: Ot.enc.Base64url.parse(process.argv[2])
   }, Ot.enc.Hex.parse("aaad3e4fd540b0f79dca95606e72bf93"), {
       mode: Ot.mode.ECB,
       padding: Ot.pad.Pkcs7
   }).toString(Ot.enc.Utf8);
console.log(u);