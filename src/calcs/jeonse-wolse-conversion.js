// 주택임대차보호법 제7조의2, 시행령 제9조: 월차임 = 전환 보증금 × 전환율 ÷ 12 (상한: min(연 10%, 기준금리+2%))
const BASE=3.00,CAP=Math.min(10,BASE+2);
function sync(){
  const j=C.radio('dir')==='j2w';
  C.$('#l1').textContent=j?'현재 전세 보증금':'현재 보증금';
  C.$('#rentBox').style.display=j?'none':'';
  C.$('label[for="newdep"]').textContent=j?'바꾼 뒤 보증금':'바꾼 뒤 보증금 (올릴 금액 포함)';
}
document.querySelectorAll('input[name="dir"]').forEach(el=>el.addEventListener('change',()=>{
  const j=C.radio('dir')==='j2w';
  C.$('#dep').value=j?'300,000,000':'50,000,000';
  C.$('#newdep').value=j?'100,000,000':'200,000,000';
  sync();
}));
C.onCalc(()=>{
  const rate=C.num('rate')/100,dep=C.num('dep'),nd=C.num('newdep');
  if(rate<=0){C.show('res','<p class="msg">전환율을 입력해 주세요.</p>');return}
  const over=rate*100>CAP+1e-9?`<p class="msg">입력한 전환율이 법정 상한 ${CAP.toFixed(2)}%보다 높습니다. 계약 기간 중이거나 갱신할 때는 상한을 넘을 수 없습니다.</p>`:'';
  if(C.radio('dir')==='j2w'){
    const conv=dep-nd;
    if(conv<=0){C.show('res','<p class="msg">바꾼 뒤 보증금이 현재 보증금보다 적어야 합니다.</p>');return}
    const m=conv*rate/12;
    C.show('res',`<div class="big">전환 후 월세<b>${C.won(m)}</b></div>${over}
    ${C.rows([['월세로 바꾸는 보증금',C.won(conv)],['전환율',`연 ${(rate*100).toFixed(2)}%`],['연간 월세 합계',C.won(m*12)],['결과','보증금 '+C.won(nd)+' / 월세 '+C.won(m),'sum']])}
    <p class="how">${C.fmt(conv)}원 × ${(rate*100).toFixed(2)}% ÷ 12 = 월 ${C.fmt(m)}원</p>`);
  }else{
    const rent=C.num('rent'),add=nd-dep;
    if(add<=0){C.show('res','<p class="msg">바꾼 뒤 보증금이 현재 보증금보다 커야 합니다.</p>');return}
    const cut=add*rate/12,left=Math.max(0,rent-cut);
    const full=dep+rent*12/rate;
    C.show('res',`<div class="big">보증금을 올린 뒤 월세<b>${C.won(left)}</b></div>${over}
    ${C.rows([['올리는 보증금',C.won(add)],['줄어드는 월세',C.won(cut)],['현재 월세',C.won(rent)],['결과','보증금 '+C.won(nd)+' / 월세 '+C.won(left),'sum'],['월세 없이 전세로 바꾸면',C.won(full)]])}`);
  }
});
sync();
C.$('#calcForm').addEventListener('reset',()=>setTimeout(sync,0));
