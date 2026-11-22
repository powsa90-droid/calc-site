// 2026년 기준 연봉 실수령액 (근로소득 간이세액 추정)
const R={np:0.0475,npMin:410000,npMax:6590000,hi:0.03595,ltc:0.1314,ei:0.009};
function earnDed(g){ // 근로소득공제 (연)
  let d;
  if(g<=5e6)d=g*0.7;else if(g<=15e6)d=3.5e6+(g-5e6)*0.4;else if(g<=45e6)d=7.5e6+(g-15e6)*0.15;else if(g<=1e8)d=12e6+(g-45e6)*0.05;else d=14.75e6+(g-1e8)*0.02;
  return Math.min(d,2e7);
}
function taxRate(t){ // 종합소득세 기본세율
  const b=[[14e6,.06,0],[5e7,.15,1.26e6],[8.8e7,.24,5.76e6],[1.5e8,.35,15.44e6],[3e8,.38,19.94e6],[5e8,.40,25.94e6],[1e9,.42,35.94e6],[Infinity,.45,65.94e6]];
  for(const[l,r,k]of b)if(t<=l)return Math.max(0,t*r-k);
}
function earnCredit(tax,g){ // 근로소득세액공제
  let c=tax<=1.3e6?tax*0.55:715000+(tax-1.3e6)*0.3;
  let lim;
  if(g<=3.3e7)lim=740000;else if(g<=7e7)lim=Math.max(660000,740000-(g-3.3e7)*0.008);else if(g<=1.2e8)lim=Math.max(500000,660000-(g-7e7)*0.5);else lim=Math.max(200000,500000-(g-1.2e8)*0.5);
  return Math.min(c,lim);
}
function kidCredit(n){if(n<=0)return 0;if(n===1)return 12500;if(n===2)return 29160;return 29160+(n-2)*25000}
function calc(gross,nontax,fam,kids){
  const taxable=Math.max(0,gross-nontax);
  const np=C.floor10(Math.min(Math.max(taxable,R.npMin),R.npMax)*R.np);
  const hi=C.floor10(taxable*R.hi);
  const ltc=C.floor10(hi*R.ltc);
  const ei=C.floor10(taxable*R.ei);
  const G=taxable*12;
  const base=Math.max(0,G-earnDed(G)-1.5e6*Math.max(1,fam)-np*12-(hi+ltc+ei)*12);
  const t=taxRate(base);
  const annual=Math.max(0,t-earnCredit(t,G));
  let it=Math.max(0,C.floor10(annual/12-kidCredit(kids)));
  const lt=C.floor10(it*0.1);
  const ded=np+hi+ltc+ei+it+lt;
  return{gross,taxable,np,hi,ltc,ei,it,lt,ded,net:gross-ded};
}
C.onCalc(()=>{
  let pay=C.num('pay');const nontax=C.num('nontax'),fam=Math.round(C.num('fam'))||1,kids=Math.round(C.num('kids'));
  if(pay<=0){C.show('res','<p class="msg">세전 금액을 입력해 주세요.</p>');return}
  const year=C.radio('basis')==='year',sev=C.radio('sev')==='1';
  const monthly=year?pay/(sev?13:12):pay;
  const r=calc(Math.round(monthly),nontax,fam,kids);
  C.show('res',`<div class="big">예상 월 실수령액<b>${C.won(r.net)}</b></div>
  <div class="big" style="margin-top:6px">연 환산 실수령액 약 ${C.won(r.net*12)}</div>
  ${C.rows([
    ['월 세전 급여',C.won(r.gross)],
    ['국민연금 (4.75%)','-'+C.won(r.np),'minus'],
    ['건강보험 (3.595%)','-'+C.won(r.hi),'minus'],
    ['장기요양보험 (건강보험료의 13.14%)','-'+C.won(r.ltc),'minus'],
    ['고용보험 (0.9%)','-'+C.won(r.ei),'minus'],
    ['근로소득세 (추정)','-'+C.won(r.it),'minus'],
    ['지방소득세 (소득세의 10%)','-'+C.won(r.lt),'minus'],
    ['공제액 합계','-'+C.won(r.ded),'minus'],
    ['월 실수령액',C.won(r.net),'sum']])}
  <p class="how">4대보험은 비과세를 뺀 월 ${C.won(r.taxable)}을 기준으로 계산했습니다. 소득세는 연간 근로소득공제·인적공제·보험료공제와 근로소득세액공제를 적용해 월로 나눈 추정치라 회사 명세서의 간이세액표 금액과 몇천 원에서 몇만 원 차이가 날 수 있습니다.</p>`);
});
