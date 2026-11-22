// 지방세법 제11조(주택 유상거래 1~3%), 제13조의2(다주택 중과 8%·12%), 지방세법 제151조(지방교육세), 농어촌특별세법 제5조
function baseRate(p){ // 퍼센트
  if(p<=6e8)return 1;
  if(p>9e8)return 3;
  return Math.round((p/1e8*2/3-3)*1e4)/1e4; // 소수점 다섯째 자리 반올림
}
C.onCalc(()=>{
  const p=C.num('price'),n=+C.$('#cnt').value,adj=C.radio('adj')==='1',big=C.radio('area')==='1';
  if(p<=0){C.show('res','<p class="msg">취득가액을 입력해 주세요.</p>');return}
  let rate,heavy=0;
  if(n===1||(n===2&&!adj)){rate=baseRate(p)}
  else if((n===2&&adj)||(n===3&&!adj)){rate=8;heavy=8}
  else{rate=12;heavy=12}
  const acq=Math.floor(p*rate/100);
  const edu=Math.floor(heavy?p*0.004:acq*0.1);
  const agr=big?Math.floor(p*(heavy===12?0.01:heavy===8?0.006:0.002)):0;
  const tot=acq+edu+agr;
  C.show('res',`<div class="big">취득세 합계 (지방교육세·농특세 포함)<b>${C.won(tot)}</b></div>
  <div class="big" style="margin-top:6px">실효 세율 ${(tot/p*100).toFixed(2)}%</div>
  ${C.rows([
    ['적용 취득세율',`${+rate.toFixed(4)}%${heavy?' (다주택 중과)':''}`],
    ['취득세',C.won(acq)],
    [`지방교육세${heavy?' (0.4%)':' (취득세의 10%)'}`,C.won(edu)],
    [`농어촌특별세${big?'':' (85㎡ 이하 비과세)'}`,C.won(agr)],
    ['합계',C.won(tot),'sum']])}
  <p class="how">취득일(잔금일)로부터 60일 안에 위택스나 시·군·구청에 신고·납부합니다. 생애최초 주택 구입 감면 등 감면은 반영하지 않았습니다.</p>`);
});
