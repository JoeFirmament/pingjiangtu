const LOG=[]; function ok(c,m){ LOG.push((c?"PASS ":"FAIL ")+m); }
setTimeout(()=>{
 try{
  const P = n => places.find(x=>x.n===n);

  // 1 拖动（不进入编辑模式，事件打在红点上）
  const p1 = P("飲馬橋"); select(p1.id,false);
  const m1 = document.querySelector('.mk[data-id="'+p1.id+'"]');
  const r1 = m1.getBoundingClientRect();
  const cx = r1.left+r1.width/2, cy = r1.top+r1.height/2;
  const x0=p1.x, y0=p1.y;
  m1.dispatchEvent(new PointerEvent("pointerdown",{clientX:cx,clientY:cy,pointerId:1,bubbles:true}));
  stage.dispatchEvent(new PointerEvent("pointermove",{clientX:cx+34,clientY:cy+34,pointerId:1,bubbles:true}));
  stage.dispatchEvent(new PointerEvent("pointerup",{clientX:cx+34,clientY:cy+34,pointerId:1,bubbles:true}));
  ok(p1.x!==x0 && p1.y!==y0, "拖动改变坐标 ("+x0+","+y0+")→("+p1.x+","+p1.y+")");
  ok(p1.fx===1, "拖动后打修正标记");
  ok(document.querySelector('.mk[data-id="'+p1.id+'"]').classList.contains("fx"), "金圈出现");

  // 2 方向键
  const p2 = P("皋橋"); select(p2.id,false); const ax=p2.x;
  window.dispatchEvent(new KeyboardEvent("keydown",{key:"ArrowRight",bubbles:true}));
  ok(p2.x===ax+1, "→ 1px ("+ax+"→"+p2.x+")");
  window.dispatchEvent(new KeyboardEvent("keydown",{key:"ArrowRight",shiftKey:true,bubbles:true}));
  ok(p2.x===ax+11, "⇧→ 10px");
  ok(fX.value==String(Math.round(p2.x)), "坐标框同步");

  // 3 贴近原字：挪歪后吸附，应落回原框中心
  select(p1.id, false);
  setPos(p1, p1.x+70, p1.y+40);
  const nb0 = nearestBox(p1);
  document.getElementById("fSnap").click();
  ok(nb0 && Math.abs(p1.x-nb0.box.x)<1.5 && Math.abs(p1.y-nb0.box.y)<1.5,
     "贴近后落在框中心 ("+p1.x+","+p1.y+") ≟ ("+nb0.box.x.toFixed(1)+","+nb0.box.y.toFixed(1)+")");
  ok(p1.fx===1, "贴近也算修正");

  // 4 重新定位
  select(p2.id,false);
  document.getElementById("fPick").click();
  ok(document.body.classList.contains("picking"), "进入拾取模式");
  const sr = stage.getBoundingClientRect();
  stage.dispatchEvent(new PointerEvent("pointerdown",{clientX:sr.left+320,clientY:sr.top+300,pointerId:1,bubbles:true}));
  ok(!document.body.classList.contains("picking"), "拾取后退出");
  const eX=(320-tx)/s, eY=(300-ty)/s;
  ok(Math.abs(p2.x-eX)<2 && Math.abs(p2.y-eY)<2, "落到点击处 ("+p2.x+","+p2.y+")");

  // 5 改已有名字：⏎ 不跳
  const id2 = p2.id;
  fName.value="皋橋甲"; fName.dispatchEvent(new Event("input"));
  fName.dispatchEvent(new KeyboardEvent("keydown",{key:"Enter",bubbles:true}));
  ok(p2.n==="皋橋甲", "改名生效");
  ok(selId===id2, "已有名字 ⏎ 不自动跳");
  ok(p2.fx===1, "改名也算修正");

  // 6 修正清单
  const fxArr = places.filter(x=>x.fx);
  ok(fxArr.length>=2, "修正清单 "+fxArr.length+" 条");

  // 7 合并时保留修正
  const store = places.map(x=>JSON.parse(JSON.stringify(x)));
  const merged = mergeSeed(store);
  const t = merged.find(x=>x.id===id2);
  ok(t && t.x===p2.x && t.y===p2.y && t.fx===1, "重建时保留你的坐标");
  ok(t && t.n==="皋橋甲", "重建时保留你的名字");

  // 8 撤销位置
  const bx=p2.x; setPos(p2, bx+50, p2.y);
  window.dispatchEvent(new KeyboardEvent("keydown",{key:"z",metaKey:true,bubbles:true}));
  ok(p2.x===bx, "⌘Z 撤销位置改动");
  ok(document.querySelector('.mk[data-id="'+id2+'"]').style.left === p2.x+"px", "撤销后红点同步回位");

  // 9 导出修正 JSON 结构
  const dump = fxArr.map(p=>({id:p.id,n:p.n||"",t:p.t||"",x:Math.round(p.x),y:Math.round(p.y)}));
  ok(dump.every(o=>typeof o.id==="string" && typeof o.x==="number"), "修正 JSON 字段完整");
 }catch(e){ LOG.push("EXC "+e.message+"\n"+(e.stack||"").split("\n").slice(0,3).join("\n")); }
 const d=document.createElement("pre");
 d.style.cssText="position:fixed;left:0;top:0;z-index:99;background:#fff;color:#111;font:12.5px/1.55 monospace;padding:10px;max-height:100%;overflow:auto;white-space:pre-wrap";
 d.textContent=LOG.join("\n"); document.body.appendChild(d);
},600);
