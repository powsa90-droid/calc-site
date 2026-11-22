// 공인중개사법 시행규칙 제20조, 서울특별시·경기도 주택 중개보수 조례 별표1 (2021.10.19 개정 요율)
const SALE=[[5e7,.006,25e4],[2e8,.005,8e5],[9e8,.004,0],[12e8,.005,0],[15e8,.006,0],[Infinity,.007,0]];
const LEASE=[[5e7,.005,2e5],[1e8,.004,3e5],[6e8,.003,0],[12e8,.004,0],[15e8,.005,0],[Infinity,.006,0]];
function sync(){
  const k=C.radio('kind');
  C.$('#amtL').textContent=k==='sale'?'매매가':k==='jeonse'?'전세 보증금':'월세 보증금';
  C.$('#rentBox').style.display=k==='wolse'?'':'none';
}
document.querySelectorAll('input[name="kind"]').forEach(el=>el.addEventListener('change',()=>{
  const k=C.radio('kind');C.$('#amt').value=k==='sale'?'500,000,000':k==='jeonse'?'300,000,000':'10,000,000';sync();
}));
C.onCalc(()=>{
  const k=C.radio('kind'),prop=C.radio('prop'),vat=parseFloat(C.radio('vat'));
  let amt=C.num('amt');const rent=k==='wolse'?C.num('rent'):0;
  if(amt<=0&&rent<=0){C.show('res','<p class="msg">금액을 입력해 주세요.</p>');return}
  let deal=amt,note='';
  if(k==='wolse'){deal=amt+rent*100;note=`보증금 + 월세 × 100 = ${C.fmt(deal)}원`;
    if(deal<5e7){deal=amt+rent*70;note=`보증금 + 월세 × 100이 5천만 원 미만이라 보증금 + 월세 × 70 = ${C.fmt(deal)}원`}}
  let rate,cap=0;
  if(prop==='house'){const t=k==='sale'?SALE:LEASE;for(const[l,r,c]of t)if(deal<l){rate=r;cap=c;break}}
  else if(prop==='officetel')rate=k==='sale'?.005:.004;
  else rate=.009;
  let fee=Math.floor(deal*rate);
  if(cap&&fee>cap)fee=cap;
  const v=Math.floor(fee*vat);
  C.show('res',`<div class="big">중개수수료 상한 (한쪽 기준)<b>${C.won(fee+v)}</b></div>
  ${C.rows([
    ['거래금액',C.won(deal)],
    ['상한요율',`${(rate*100).toFixed(1)}%${prop==='etc'?' 이내 협의':''}`],
    ['한도액',cap?C.won(cap):'없음'],
    ['중개보수',C.won(fee)],
    [`부가가치세 (${vat*100}%)`,C.won(v)],
    ['합계',C.won(fee+v),'sum']])}
  ${note?`<p class="how">${note}</p>`:''}
  <p class="how">계산 결과는 받을 수 있는 최대 금액이며, 이 범위 안에서 중개사와 협의해 정합니다. 매도인과 매수인(임대인과 임차인)이 각각 냅니다.</p>`);
});
C.$('#calcForm').addEventListener('reset',()=>setTimeout(sync,0));
sync();
