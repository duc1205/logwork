;
/* module-key = 'com.atlassian.auiplugin:split_aui.splitchunk.vendors--9c8c8c1546', location = 'aui.chunk.5dea31f049d6c4f0c3de--2aa0019581c68055c6ea.js' */
(window.__auiJsonp=window.__auiJsonp||[]).push([["aui.splitchunk.vendors--9c8c8c1546"],{lSwU:function(n,o,i){var p,e,u;e=[i("oDIA"),i("O+lX")],void 0===(u="function"==typeof(p=function(n){return n.ui.plugin={add:function(o,i,p){var e,u=n.ui[o].prototype;for(e in p)u.plugins[e]=u.plugins[e]||[],u.plugins[e].push([i,p[e]])},call:function(n,o,i,p){var e,u=n.plugins[o];if(u&&(p||n.element[0].parentNode&&11!==n.element[0].parentNode.nodeType))for(e=0;e<u.length;e++)n.options[u[e][0]]&&u[e][1].apply(n.element,i)}}})?p.apply(o,e):p)||(n.exports=u)}}]);
//# sourceMappingURL=aui.chunk.5dea31f049d6c4f0c3de--2aa0019581c68055c6ea.js.map;
;
/* module-key = 'com.atlassian.auiplugin:split_aui.splitchunk.vendors--06bc6ae5d7', location = 'aui.chunk.604fd3e8f834244da4a6--3b7718afeb87134077c9.js' */
(window.__auiJsonp=window.__auiJsonp||[]).push([["aui.splitchunk.vendors--06bc6ae5d7"],{"0Hbr":function(t,e,s){var i,o,n;o=[s("oDIA"),s("O+lX")],void 0===(n="function"==typeof(i=function(t){return t.ui.safeActiveElement=function(t){var e;try{e=t.activeElement}catch(s){e=t.body}return e||(e=t.body),e.nodeName||(e=t.body),e}})?i.apply(e,o):i)||(t.exports=n)},pTG0:function(t,e,s){var i,o,n;o=[s("oDIA"),s("O+lX")],void 0===(n="function"==typeof(i=function(t){return t.ui.safeBlur=function(e){e&&"body"!==e.nodeName.toLowerCase()&&t(e).trigger("blur")}})?i.apply(e,o):i)||(t.exports=n)},"z+ct":function(t,e,s){var i,o,n;o=[s("oDIA"),s("XPYc"),s("5h+3"),s("lSwU"),s("0Hbr"),s("pTG0"),s("0kPy"),s("O+lX"),s("yIBB")],void 0===(n="function"==typeof(i=function(t){return t.widget("ui.draggable",t.ui.mouse,{version:"1.12.1",widgetEventPrefix:"drag",options:{addClasses:!0,appendTo:"parent",axis:!1,connectToSortable:!1,containment:!1,cursor:"auto",cursorAt:!1,grid:!1,handle:!1,helper:"original",iframeFix:!1,opacity:!1,refreshPositions:!1,revert:!1,revertDuration:500,scope:"default",scroll:!0,scrollSensitivity:20,scrollSpeed:20,snap:!1,snapMode:"both",snapTolerance:20,stack:!1,zIndex:!1,drag:null,start:null,stop:null},_create:function(){"original"===this.options.helper&&this._setPositionRelative(),this.options.addClasses&&this._addClass("ui-draggable"),this._setHandleClassName(),this._mouseInit()},_setOption:function(t,e){this._super(t,e),"handle"===t&&(this._removeHandleClassName(),this._setHandleClassName())},_destroy:function(){(this.helper||this.element).is(".ui-draggable-dragging")?this.destroyOnClear=!0:(this._removeHandleClassName(),this._mouseDestroy())},_mouseCapture:function(e){var s=this.options;return!(this.helper||s.disabled||t(e.target).closest(".ui-resizable-handle").length>0||(this.handle=this._getHandle(e),!this.handle||(this._blurActiveElement(e),this._blockFrames(!0===s.iframeFix?"iframe":s.iframeFix),0)))},_blockFrames:function(e){this.iframeBlocks=this.document.find(e).map(function(){var e=t(this);return t("<div>").css("position","absolute").appendTo(e.parent()).outerWidth(e.outerWidth()).outerHeight(e.outerHeight()).offset(e.offset())[0]})},_unblockFrames:function(){this.iframeBlocks&&(this.iframeBlocks.remove(),delete this.iframeBlocks)},_blurActiveElement:function(e){var s=t.ui.safeActiveElement(this.document[0]);t(e.target).closest(s).length||t.ui.safeBlur(s)},_mouseStart:function(e){var s=this.options;return this.helper=this._createHelper(e),this._addClass(this.helper,"ui-draggable-dragging"),this._cacheHelperProportions(),t.ui.ddmanager&&(t.ui.ddmanager.current=this),this._cacheMargins(),this.cssPosition=this.helper.css("position"),this.scrollParent=this.helper.scrollParent(!0),this.offsetParent=this.helper.offsetParent(),this.hasFixedAncestor=this.helper.parents().filter(function(){return"fixed"===t(this).css("position")}).length>0,this.positionAbs=this.element.offset(),this._refreshOffsets(e),this.originalPosition=this.position=this._generatePosition(e,!1),this.originalPageX=e.pageX,this.originalPageY=e.pageY,s.cursorAt&&this._adjustOffsetFromHelper(s.cursorAt),this._setContainment(),!1===this._trigger("start",e)?(this._clear(),!1):(this._cacheHelperProportions(),t.ui.ddmanager&&!s.dropBehaviour&&t.ui.ddmanager.prepareOffsets(this,e),this._mouseDrag(e,!0),t.ui.ddmanager&&t.ui.ddmanager.dragStart(this,e),!0)},_refreshOffsets:function(t){this.offset={top:this.positionAbs.top-this.margins.top,left:this.positionAbs.left-this.margins.left,scroll:!1,parent:this._getParentOffset(),relative:this._getRelativeOffset()},this.offset.click={left:t.pageX-this.offset.left,top:t.pageY-this.offset.top}},_mouseDrag:function(e,s){if(this.hasFixedAncestor&&(this.offset.parent=this._getParentOffset()),this.position=this._generatePosition(e,!0),this.positionAbs=this._convertPositionTo("absolute"),!s){var i=this._uiHash();if(!1===this._trigger("drag",e,i))return this._mouseUp(new t.Event("mouseup",e)),!1;this.position=i.position}return this.helper[0].style.left=this.position.left+"px",this.helper[0].style.top=this.position.top+"px",t.ui.ddmanager&&t.ui.ddmanager.drag(this,e),!1},_mouseStop:function(e){var s=this,i=!1;return t.ui.ddmanager&&!this.options.dropBehaviour&&(i=t.ui.ddmanager.drop(this,e)),this.dropped&&(i=this.dropped,this.dropped=!1),"invalid"===this.options.revert&&!i||"valid"===this.options.revert&&i||!0===this.options.revert||t.isFunction(this.options.revert)&&this.options.revert.call(this.element,i)?t(this.helper).animate(this.originalPosition,parseInt(this.options.revertDuration,10),function(){!1!==s._trigger("stop",e)&&s._clear()}):!1!==this._trigger("stop",e)&&this._clear(),!1},_mouseUp:function(e){return this._unblockFrames(),t.ui.ddmanager&&t.ui.ddmanager.dragStop(this,e),this.handleElement.is(e.target)&&this.element.trigger("focus"),t.ui.mouse.prototype._mouseUp.call(this,e)},cancel:function(){return this.helper.is(".ui-draggable-dragging")?this._mouseUp(new t.Event("mouseup",{target:this.element[0]})):this._clear(),this},_getHandle:function(e){return!this.options.handle||!!t(e.target).closest(this.element.find(this.options.handle)).length},_setHandleClassName:function(){this.handleElement=this.options.handle?this.element.find(this.options.handle):this.element,this._addClass(this.handleElement,"ui-draggable-handle")},_removeHandleClassName:function(){this._removeClass(this.handleElement,"ui-draggable-handle")},_createHelper:function(e){var s=this.options,i=t.isFunction(s.helper),o=i?t(s.helper.apply(this.element[0],[e])):"clone"===s.helper?this.element.clone().removeAttr("id"):this.element;return o.parents("body").length||o.appendTo("parent"===s.appendTo?this.element[0].parentNode:s.appendTo),i&&o[0]===this.element[0]&&this._setPositionRelative(),o[0]===this.element[0]||/(fixed|absolute)/.test(o.css("position"))||o.css("position","absolute"),o},_setPositionRelative:function(){/^(?:r|a|f)/.test(this.element.css("position"))||(this.element[0].style.position="relative")},_adjustOffsetFromHelper:function(e){"string"==typeof e&&(e=e.split(" ")),t.isArray(e)&&(e={left:+e[0],top:+e[1]||0}),"left"in e&&(this.offset.click.left=e.left+this.margins.left),"right"in e&&(this.offset.click.left=this.helperProportions.width-e.right+this.margins.left),"top"in e&&(this.offset.click.top=e.top+this.margins.top),"bottom"in e&&(this.offset.click.top=this.helperProportions.height-e.bottom+this.margins.top)},_isRootNode:function(t){return/(html|body)/i.test(t.tagName)||t===this.document[0]},_getParentOffset:function(){var e=this.offsetParent.offset(),s=this.document[0];return"absolute"===this.cssPosition&&this.scrollParent[0]!==s&&t.contains(this.scrollParent[0],this.offsetParent[0])&&(e.left+=this.scrollParent.scrollLeft(),e.top+=this.scrollParent.scrollTop()),this._isRootNode(this.offsetParent[0])&&(e={top:0,left:0}),{top:e.top+(parseInt(this.offsetParent.css("borderTopWidth"),10)||0),left:e.left+(parseInt(this.offsetParent.css("borderLeftWidth"),10)||0)}},_getRelativeOffset:function(){if("relative"!==this.cssPosition)return{top:0,left:0};var t=this.element.position(),e=this._isRootNode(this.scrollParent[0]);return{top:t.top-(parseInt(this.helper.css("top"),10)||0)+(e?0:this.scrollParent.scrollTop()),left:t.left-(parseInt(this.helper.css("left"),10)||0)+(e?0:this.scrollParent.scrollLeft())}},_cacheMargins:function(){this.margins={left:parseInt(this.element.css("marginLeft"),10)||0,top:parseInt(this.element.css("marginTop"),10)||0,right:parseInt(this.element.css("marginRight"),10)||0,bottom:parseInt(this.element.css("marginBottom"),10)||0}},_cacheHelperProportions:function(){this.helperProportions={width:this.helper.outerWidth(),height:this.helper.outerHeight()}},_setContainment:function(){var e,s,i,o=this.options,n=this.document[0];this.relativeContainer=null,o.containment?"window"!==o.containment?"document"!==o.containment?o.containment.constructor!==Array?("parent"===o.containment&&(o.containment=this.helper[0].parentNode),(i=(s=t(o.containment))[0])&&(e=/(scroll|auto)/.test(s.css("overflow")),this.containment=[(parseInt(s.css("borderLeftWidth"),10)||0)+(parseInt(s.css("paddingLeft"),10)||0),(parseInt(s.css("borderTopWidth"),10)||0)+(parseInt(s.css("paddingTop"),10)||0),(e?Math.max(i.scrollWidth,i.offsetWidth):i.offsetWidth)-(parseInt(s.css("borderRightWidth"),10)||0)-(parseInt(s.css("paddingRight"),10)||0)-this.helperProportions.width-this.margins.left-this.margins.right,(e?Math.max(i.scrollHeight,i.offsetHeight):i.offsetHeight)-(parseInt(s.css("borderBottomWidth"),10)||0)-(parseInt(s.css("paddingBottom"),10)||0)-this.helperProportions.height-this.margins.top-this.margins.bottom],this.relativeContainer=s)):this.containment=o.containment:this.containment=[0,0,t(n).width()-this.helperProportions.width-this.margins.left,(t(n).height()||n.body.parentNode.scrollHeight)-this.helperProportions.height-this.margins.top]:this.containment=[t(window).scrollLeft()-this.offset.relative.left-this.offset.parent.left,t(window).scrollTop()-this.offset.relative.top-this.offset.parent.top,t(window).scrollLeft()+t(window).width()-this.helperProportions.width-this.margins.left,t(window).scrollTop()+(t(window).height()||n.body.parentNode.scrollHeight)-this.helperProportions.height-this.margins.top]:this.containment=null},_convertPositionTo:function(t,e){e||(e=this.position);var s="absolute"===t?1:-1,i=this._isRootNode(this.scrollParent[0]);return{top:e.top+this.offset.relative.top*s+this.offset.parent.top*s-("fixed"===this.cssPosition?-this.offset.scroll.top:i?0:this.offset.scroll.top)*s,left:e.left+this.offset.relative.left*s+this.offset.parent.left*s-("fixed"===this.cssPosition?-this.offset.scroll.left:i?0:this.offset.scroll.left)*s}},_generatePosition:function(t,e){var s,i,o,n,r=this.options,l=this._isRootNode(this.scrollParent[0]),a=t.pageX,h=t.pageY;return l&&this.offset.scroll||(this.offset.scroll={top:this.scrollParent.scrollTop(),left:this.scrollParent.scrollLeft()}),e&&(this.containment&&(this.relativeContainer?(i=this.relativeContainer.offset(),s=[this.containment[0]+i.left,this.containment[1]+i.top,this.containment[2]+i.left,this.containment[3]+i.top]):s=this.containment,t.pageX-this.offset.click.left<s[0]&&(a=s[0]+this.offset.click.left),t.pageY-this.offset.click.top<s[1]&&(h=s[1]+this.offset.click.top),t.pageX-this.offset.click.left>s[2]&&(a=s[2]+this.offset.click.left),t.pageY-this.offset.click.top>s[3]&&(h=s[3]+this.offset.click.top)),r.grid&&(o=r.grid[1]?this.originalPageY+Math.round((h-this.originalPageY)/r.grid[1])*r.grid[1]:this.originalPageY,h=s?o-this.offset.click.top>=s[1]||o-this.offset.click.top>s[3]?o:o-this.offset.click.top>=s[1]?o-r.grid[1]:o+r.grid[1]:o,n=r.grid[0]?this.originalPageX+Math.round((a-this.originalPageX)/r.grid[0])*r.grid[0]:this.originalPageX,a=s?n-this.offset.click.left>=s[0]||n-this.offset.click.left>s[2]?n:n-this.offset.click.left>=s[0]?n-r.grid[0]:n+r.grid[0]:n),"y"===r.axis&&(a=this.originalPageX),"x"===r.axis&&(h=this.originalPageY)),{top:h-this.offset.click.top-this.offset.relative.top-this.offset.parent.top+("fixed"===this.cssPosition?-this.offset.scroll.top:l?0:this.offset.scroll.top),left:a-this.offset.click.left-this.offset.relative.left-this.offset.parent.left+("fixed"===this.cssPosition?-this.offset.scroll.left:l?0:this.offset.scroll.left)}},_clear:function(){this._removeClass(this.helper,"ui-draggable-dragging"),this.helper[0]===this.element[0]||this.cancelHelperRemoval||this.helper.remove(),this.helper=null,this.cancelHelperRemoval=!1,this.destroyOnClear&&this.destroy()},_trigger:function(e,s,i){return i=i||this._uiHash(),t.ui.plugin.call(this,e,[s,i,this],!0),/^(drag|start|stop)/.test(e)&&(this.positionAbs=this._convertPositionTo("absolute"),i.offset=this.positionAbs),t.Widget.prototype._trigger.call(this,e,s,i)},plugins:{},_uiHash:function(){return{helper:this.helper,position:this.position,originalPosition:this.originalPosition,offset:this.positionAbs}}}),t.ui.plugin.add("draggable","connectToSortable",{start:function(e,s,i){var o=t.extend({},s,{item:i.element});i.sortables=[],t(i.options.connectToSortable).each(function(){var s=t(this).sortable("instance");s&&!s.options.disabled&&(i.sortables.push(s),s.refreshPositions(),s._trigger("activate",e,o))})},stop:function(e,s,i){var o=t.extend({},s,{item:i.element});i.cancelHelperRemoval=!1,t.each(i.sortables,function(){this.isOver?(this.isOver=0,i.cancelHelperRemoval=!0,this.cancelHelperRemoval=!1,this._storedCSS={position:this.placeholder.css("position"),top:this.placeholder.css("top"),left:this.placeholder.css("left")},this._mouseStop(e),this.options.helper=this.options._helper):(this.cancelHelperRemoval=!0,this._trigger("deactivate",e,o))})},drag:function(e,s,i){t.each(i.sortables,function(){var o=!1,n=this;n.positionAbs=i.positionAbs,n.helperProportions=i.helperProportions,n.offset.click=i.offset.click,n._intersectsWith(n.containerCache)&&(o=!0,t.each(i.sortables,function(){return this.positionAbs=i.positionAbs,this.helperProportions=i.helperProportions,this.offset.click=i.offset.click,this!==n&&this._intersectsWith(this.containerCache)&&t.contains(n.element[0],this.element[0])&&(o=!1),o})),o?(n.isOver||(n.isOver=1,i._parent=s.helper.parent(),n.currentItem=s.helper.appendTo(n.element).data("ui-sortable-item",!0),n.options._helper=n.options.helper,n.options.helper=function(){return s.helper[0]},e.target=n.currentItem[0],n._mouseCapture(e,!0),n._mouseStart(e,!0,!0),n.offset.click.top=i.offset.click.top,n.offset.click.left=i.offset.click.left,n.offset.parent.left-=i.offset.parent.left-n.offset.parent.left,n.offset.parent.top-=i.offset.parent.top-n.offset.parent.top,i._trigger("toSortable",e),i.dropped=n.element,t.each(i.sortables,function(){this.refreshPositions()}),i.currentItem=i.element,n.fromOutside=i),n.currentItem&&(n._mouseDrag(e),s.position=n.position)):n.isOver&&(n.isOver=0,n.cancelHelperRemoval=!0,n.options._revert=n.options.revert,n.options.revert=!1,n._trigger("out",e,n._uiHash(n)),n._mouseStop(e,!0),n.options.revert=n.options._revert,n.options.helper=n.options._helper,n.placeholder&&n.placeholder.remove(),s.helper.appendTo(i._parent),i._refreshOffsets(e),s.position=i._generatePosition(e,!0),i._trigger("fromSortable",e),i.dropped=!1,t.each(i.sortables,function(){this.refreshPositions()}))})}}),t.ui.plugin.add("draggable","cursor",{start:function(e,s,i){var o=t("body"),n=i.options;o.css("cursor")&&(n._cursor=o.css("cursor")),o.css("cursor",n.cursor)},stop:function(e,s,i){var o=i.options;o._cursor&&t("body").css("cursor",o._cursor)}}),t.ui.plugin.add("draggable","opacity",{start:function(e,s,i){var o=t(s.helper),n=i.options;o.css("opacity")&&(n._opacity=o.css("opacity")),o.css("opacity",n.opacity)},stop:function(e,s,i){var o=i.options;o._opacity&&t(s.helper).css("opacity",o._opacity)}}),t.ui.plugin.add("draggable","scroll",{start:function(t,e,s){s.scrollParentNotHidden||(s.scrollParentNotHidden=s.helper.scrollParent(!1)),s.scrollParentNotHidden[0]!==s.document[0]&&"HTML"!==s.scrollParentNotHidden[0].tagName&&(s.overflowOffset=s.scrollParentNotHidden.offset())},drag:function(e,s,i){var o=i.options,n=!1,r=i.scrollParentNotHidden[0],l=i.document[0];r!==l&&"HTML"!==r.tagName?(o.axis&&"x"===o.axis||(i.overflowOffset.top+r.offsetHeight-e.pageY<o.scrollSensitivity?r.scrollTop=n=r.scrollTop+o.scrollSpeed:e.pageY-i.overflowOffset.top<o.scrollSensitivity&&(r.scrollTop=n=r.scrollTop-o.scrollSpeed)),o.axis&&"y"===o.axis||(i.overflowOffset.left+r.offsetWidth-e.pageX<o.scrollSensitivity?r.scrollLeft=n=r.scrollLeft+o.scrollSpeed:e.pageX-i.overflowOffset.left<o.scrollSensitivity&&(r.scrollLeft=n=r.scrollLeft-o.scrollSpeed))):(o.axis&&"x"===o.axis||(e.pageY-t(l).scrollTop()<o.scrollSensitivity?n=t(l).scrollTop(t(l).scrollTop()-o.scrollSpeed):t(window).height()-(e.pageY-t(l).scrollTop())<o.scrollSensitivity&&(n=t(l).scrollTop(t(l).scrollTop()+o.scrollSpeed))),o.axis&&"y"===o.axis||(e.pageX-t(l).scrollLeft()<o.scrollSensitivity?n=t(l).scrollLeft(t(l).scrollLeft()-o.scrollSpeed):t(window).width()-(e.pageX-t(l).scrollLeft())<o.scrollSensitivity&&(n=t(l).scrollLeft(t(l).scrollLeft()+o.scrollSpeed)))),!1!==n&&t.ui.ddmanager&&!o.dropBehaviour&&t.ui.ddmanager.prepareOffsets(i,e)}}),t.ui.plugin.add("draggable","snap",{start:function(e,s,i){var o=i.options;i.snapElements=[],t(o.snap.constructor!==String?o.snap.items||":data(ui-draggable)":o.snap).each(function(){var e=t(this),s=e.offset();this!==i.element[0]&&i.snapElements.push({item:this,width:e.outerWidth(),height:e.outerHeight(),top:s.top,left:s.left})})},drag:function(e,s,i){var o,n,r,l,a,h,p,c,f,d,g=i.options,u=g.snapTolerance,m=s.offset.left,v=m+i.helperProportions.width,_=s.offset.top,P=_+i.helperProportions.height;for(f=i.snapElements.length-1;f>=0;f--)h=(a=i.snapElements[f].left-i.margins.left)+i.snapElements[f].width,c=(p=i.snapElements[f].top-i.margins.top)+i.snapElements[f].height,v<a-u||m>h+u||P<p-u||_>c+u||!t.contains(i.snapElements[f].item.ownerDocument,i.snapElements[f].item)?(i.snapElements[f].snapping&&i.options.snap.release&&i.options.snap.release.call(i.element,e,t.extend(i._uiHash(),{snapItem:i.snapElements[f].item})),i.snapElements[f].snapping=!1):("inner"!==g.snapMode&&(o=Math.abs(p-P)<=u,n=Math.abs(c-_)<=u,r=Math.abs(a-v)<=u,l=Math.abs(h-m)<=u,o&&(s.position.top=i._convertPositionTo("relative",{top:p-i.helperProportions.height,left:0}).top),n&&(s.position.top=i._convertPositionTo("relative",{top:c,left:0}).top),r&&(s.position.left=i._convertPositionTo("relative",{top:0,left:a-i.helperProportions.width}).left),l&&(s.position.left=i._convertPositionTo("relative",{top:0,left:h}).left)),d=o||n||r||l,"outer"!==g.snapMode&&(o=Math.abs(p-_)<=u,n=Math.abs(c-P)<=u,r=Math.abs(a-m)<=u,l=Math.abs(h-v)<=u,o&&(s.position.top=i._convertPositionTo("relative",{top:p,left:0}).top),n&&(s.position.top=i._convertPositionTo("relative",{top:c-i.helperProportions.height,left:0}).top),r&&(s.position.left=i._convertPositionTo("relative",{top:0,left:a}).left),l&&(s.position.left=i._convertPositionTo("relative",{top:0,left:h-i.helperProportions.width}).left)),!i.snapElements[f].snapping&&(o||n||r||l||d)&&i.options.snap.snap&&i.options.snap.snap.call(i.element,e,t.extend(i._uiHash(),{snapItem:i.snapElements[f].item})),i.snapElements[f].snapping=o||n||r||l||d)}}),t.ui.plugin.add("draggable","stack",{start:function(e,s,i){var o,n=i.options,r=t.makeArray(t(n.stack)).sort(function(e,s){return(parseInt(t(e).css("zIndex"),10)||0)-(parseInt(t(s).css("zIndex"),10)||0)});r.length&&(o=parseInt(t(r[0]).css("zIndex"),10)||0,t(r).each(function(e){t(this).css("zIndex",o+e)}),this.css("zIndex",o+r.length))}}),t.ui.plugin.add("draggable","zIndex",{start:function(e,s,i){var o=t(s.helper),n=i.options;o.css("zIndex")&&(n._zIndex=o.css("zIndex")),o.css("zIndex",n.zIndex)},stop:function(e,s,i){var o=i.options;o._zIndex&&t(s.helper).css("zIndex",o._zIndex)}}),t.ui.draggable})?i.apply(e,o):i)||(t.exports=n)}}]);
//# sourceMappingURL=aui.chunk.604fd3e8f834244da4a6--3b7718afeb87134077c9.js.map;
;
/* module-key = 'com.atlassian.auiplugin:split_aui.splitchunk.vendors--37ccb8d673', location = 'aui.chunk.4b05cf846e0e94d77dfd--5d9e973ef896189af966.js' */
(window.__auiJsonp=window.__auiJsonp||[]).push([["aui.splitchunk.vendors--37ccb8d673"],{D3y7:function(e,i,a){var n,o;void 0===(o="function"==typeof(n=["jquery","./data","./disable-selection","./focusable","./form","./ie","./keycode","./labels","./jquery-1-7","./plugin","./safe-active-element","./safe-blur","./scroll-parent","./tabbable","./unique-id","./version"])?n.call(i,a,i,e):n)||(e.exports=o)}}]);
//# sourceMappingURL=aui.chunk.4b05cf846e0e94d77dfd--5d9e973ef896189af966.js.map;
;
/* module-key = 'com.atlassian.auiplugin:split_aui.splitchunk.16f099a0da', location = 'aui.chunk.b8d538420d4f10a69910--057b5af785a9bd94d156.js' */
(window.__auiJsonp=window.__auiJsonp||[]).push([["aui.splitchunk.16f099a0da"],{jJ4L:function(i,n,o){"use strict";o("FStl"),o("Q0fs"),o("oTK+"),o("S3ao"),o("HNID"),o("YQ7q"),o("xjlV")},xjlV:function(i,n,o){}}]);
//# sourceMappingURL=aui.chunk.b8d538420d4f10a69910--057b5af785a9bd94d156.js.map;
;
/* module-key = 'com.atlassian.auiplugin:split_aui.component.restful-table', location = 'aui.chunk.7cfb006e493d8523a32c--d5a44e16a3b7bfa2e178.js' */
(window.__auiJsonp=window.__auiJsonp||[]).push([["aui.component.restful-table"],{"47Al":function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var i="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},n=u(s("+x/D"));s("lyon");var a=u(s("qT0E")),o=u(s("vRZA")),r=u(s("oLrn")),l=u(s("HOn5")),d=(u(s("HH5i")),s("t6J+"));function u(e){return e&&e.__esModule?e:{default:e}}var c=-1!==navigator.userAgent.toLowerCase().indexOf("firefox");t.default=a.default.View.extend({tagName:"tr",events:{focusin:"_focus",click:"_focus",keyup:"_handleKeyUpEvent"},initialize:function(e){var t=this;this.$el=(0,n.default)(this.el),this._event=l.default,this.classNames=o.default,this.dataKeys=r.default,this.columns=e.columns,this.isCreateRow=e.isCreateRow,this.allowReorder=e.allowReorder,this.events["click ."+this.classNames.CANCEL]="_cancel",this.delegateEvents(),e.isUpdateMode?this.isUpdateMode=!0:(this._modelClass=e.model,this.model=new this._modelClass),this.fieldFocusSelector=e.fieldFocusSelector,this.on(this._event.CANCEL,function(){return t.disabled=!0}).on(this._event.SAVE,function(e){return!t.disabled&&t.submit(e)}).on(this._event.FOCUS,function(e){return t.focus(e)}).on(this._event.BLUR,function(){t.$el.removeClass(t.classNames.FOCUSED),t.disable()}).on(this._event.SUBMIT_STARTED,function(){return t._submitStarted()}).on(this._event.SUBMIT_FINISHED,function(){return t._submitFinished()})},defaultColumnRenderer:function(e){return!1!==e.allowEdit?(0,n.default)("<input type='text' />").addClass("text").attr({name:e.name,value:e.value}):e.value?document.createTextNode(e.value):void 0},renderDragHandle:function(){return'<span class="'+this.classNames.DRAG_HANDLE+'"></span></td>'},_handleKeyUpEvent:function(e){27===e.keyCode&&this.trigger(this._event.CANCEL)},_cancel:function(e){return this.trigger(this._event.CANCEL),e.preventDefault(),this},_submitStarted:function(){return this.submitting=!0,this.showLoading().disable().delegateEvents({}),this},_submitFinished:function(){return this.submitting=!1,this.hideLoading().enable().delegateEvents(this.events),this},_focus:function(e){return this.hasFocus()||this.trigger(this._event.FOCUS,e.target.name),this},hasFocus:function(){return this.$el.hasClass(this.classNames.FOCUSED)},focus:function(e){var t,s;return this.enable(),t=e?this.$el.find(this.fieldFocusSelector(e)):0===(s=this.$el.find(this.classNames.ERROR+":first")).length?this.$el.find(":input:text:first"):s.parent().find(":input"),this.$el.addClass(this.classNames.FOCUSED),t.focus().trigger("select"),this},disable:function(){var e,t;return c&&(t=this.$el.find(":submit")).length&&(e=(0,n.default)("<input type='submit' class='"+this.classNames.SUBMIT+"' />").addClass(t.attr("class")).val(t.val()).data(this.dataKeys.ENABLED_SUBMIT,t),t.replaceWith(e)),this.$el.addClass(this.classNames.DISABLED).find(":submit").attr("disabled","disabled"),this},enable:function(){var e,t;return c&&(t=(e=this.$el.find(this.classNames.SUBMIT)).data(this.dataKeys.ENABLED_SUBMIT))&&e.length&&e.replaceWith(t),this.$el.removeClass(this.classNames.DISABLED).find(":submit").removeAttr("disabled"),this},showLoading:function(){return(0,d.appendStatusSpinner)(this.$el),this},hideLoading:function(){return(0,d.removeStatusSpinner)(this.$el),this},hasUpdates:function(){return!!this.mapSubmitParams(this.serializeObject())},serializeObject:function(){var e=this.$el;return e.serializeObject?e.serializeObject():e.serialize()},mapSubmitParams:function(e){return this.model.changedAttributes(e)},submit:function(e){var t,s=this;if(document.activeElement!==window&&(0,n.default)(document.activeElement).blur(),this.isUpdateMode){if(!(t=this.mapSubmitParams(this.serializeObject())))return s.trigger(s._event.CANCEL)}else this.model.clear(),t=this.mapSubmitParams(this.serializeObject());return this.trigger(this._event.SUBMIT_STARTED),this.model.save(t,{success:function(){s.isUpdateMode?s.trigger(s._event.UPDATED,s.model,e):(s.trigger(s._event.CREATED,s.model.toJSON()),s.model=new s._modelClass,s.render({errors:{},values:{}}),s.trigger(s._event.FOCUS)),s.trigger(s._event.SUBMIT_FINISHED)},error:function(e,t,i){400===i.status&&(s.renderErrors(t.errors),s.trigger(s._event.VALIDATION_ERROR,t.errors)),s.trigger(s._event.SUBMIT_FINISHED)},silent:!0}),this},renderError:function(e,t){return(0,n.default)("<div />").attr("data-field",e).addClass(this.classNames.ERROR).text(t)},renderErrors:function(e){var t=this;return this.$("."+this.classNames.ERROR).remove(),e&&n.default.each(e,function(e,s){t.$el.find("[name='"+e+"']").closest("td").append(t.renderError(e,s))}),this},render:function(e){var t=this;return this.$el.empty(),this.allowReorder&&(0,n.default)('<td  class="'+this.classNames.ORDER+'" />').append(this.renderDragHandle()).appendTo(t.$el),n.default.each(this.columns,function(s,a){var o,r,l=e.values[a.id],d=[{name:a.id,value:l,allowEdit:a.allowEdit},e.values,t.model];l&&t.$el.attr("data-"+a.id,l),o=t.isCreateRow&&a.createView?new a.createView({model:t.model}).render(d[0]):a.editView?new a.editView({model:t.model}).render(d[0]):t.defaultColumnRenderer.apply(t,d),r=(0,n.default)("<td />"),"object"===(void 0===o?"undefined":i(o))&&o.done?o.done(function(e){r.append(e)}):r.append(o),a.styleClass&&r.addClass(a.styleClass),r.appendTo(t.$el)}),this.$el.append(this.renderOperations(e.update,e.values)).addClass(this.classNames.ROW+" "+this.classNames.EDIT_ROW),this.trigger(this._event.RENDER,this.$el,e.values),this.$el.trigger(this._event.CONTENT_REFRESHED,[this.$el]),this},renderOperations:function(e){var t=(0,n.default)('<td class="aui-restfultable-operations" />');return e?t.append((0,n.default)('<input class="aui-button" type="submit" />').attr({accesskey:this.submitAccessKey,value:"Update"})).append((0,n.default)('<a class="aui-button aui-button-link" href="#" />').addClass(this.classNames.CANCEL).text("Cancel").attr({accesskey:this.cancelAccessKey})):t.append((0,n.default)('<input class="aui-button" type="submit" />').attr({accesskey:this.submitAccessKey,value:"Add"})),t.add((0,n.default)('<td class="'+this.classNames.STATUS+'" />'))}}),e.exports=t.default},"5G0d":function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var i="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},n=d(s("+x/D")),a=s("anNl"),o=d(s("QFBp")),r=d(s("qT0E")),l=d(s("HOn5"));function d(e){return e&&e.__esModule?e:{default:e}}var u=r.default.Model.extend({sync:function(e,t,s){var i=this,n=s.error;return s.error=function(e){i._serverErrorHandler(e,this),n&&n.apply(this,arguments)},r.default.sync.apply(r.default,arguments)},save:function(e,t){var s,i=this,a=(t=t||{}).error,o=t.success;t.error=function(e,t){var s=n.default.parseJSON(t.responseText||t.data);a&&a.call(i,i,s,t)},this.isNew()?r.default.Model.prototype.save.call(this,e,t):e&&((s=new(u.extend({url:this.url()}))({id:this.id})).save=r.default.Model.prototype.save,t.success=function(e,t){i.clear().set(e.toJSON()),o&&o.call(i,i,t)},s.save(e,t))},destroy:function(e){e=e||{};var t=this,s=this.url();return n.default.ajax({url:s,type:"DELETE",dataType:"json",data:e.data||{},contentType:"application/json",success:function(s){t.collection&&t.collection.remove(t),e.success&&e.success.call(t,s)},error:function(s){t._serverErrorHandler(s,this),e.error&&e.error.call(t,s)}}),this},changedAttributes:function(e){var t={},s=this.toJSON();if(n.default.each(e,function(e,a){s[e]?s[e]&&s[e]!==a&&("object"===(void 0===a?"undefined":i(a))&&o.default.isEqual(a,s[e])||(t[e]=a)):"string"==typeof a?""!==n.default.trim(a)&&(t[e]=a):n.default.isArray(a)?0!==a.length&&(t[e]=a):t[e]=a}),!o.default.isEmpty(t))return this.addExpand(t),t},addExpand:function(e){},_serverErrorHandler:function(e,t){var s;400!==e.status&&(s=n.default.parseJSON(e.responseText||e.data),(0,a.triggerEvtForInst)(l.default.SERVER_ERROR,this,[s,e,t]))},fetch:function(e){e=e||{},this.clear(),r.default.Model.prototype.fetch.call(this,e)}});t.default=u,e.exports=t.default},"6kG1":function(e,t,s){},G3cN:function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0}),t.RestfulTable=void 0;var i=s("JSE0");Object.defineProperty(t,"RestfulTable",{enumerable:!0,get:function(){return function(e){return e&&e.__esModule?e:{default:e}}(i).default}}),s("jJ4L"),s("6kG1")},HOn5:function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0}),t.default={REORDER_SUCCESS:"RestfulTable.reorderSuccess",ROW_ADDED:"RestfulTable.rowAdded",ROW_REMOVED:"RestfulTable.rowRemoved",EDIT_ROW:"RestfulTable.switchedToEditMode",SERVER_ERROR:"RestfulTable.serverError",CREATED:"created",UPDATED:"updated",FOCUS:"focus",BLUR:"blur",SUBMIT:"submit",SAVE:"save",MODAL:"modal",MODELESS:"modeless",CANCEL:"cancel",CONTENT_REFRESHED:"contentRefreshed",RENDER:"render",FINISHED_EDITING:"finishedEditing",VALIDATION_ERROR:"validationError",SUBMIT_STARTED:"submitStarted",SUBMIT_FINISHED:"submitFinished",INITIALIZED:"initialized",ROW_INITIALIZED:"rowInitialized",ROW_EDIT:"editRow"},e.exports=t.default},JSE0:function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var i=R(s("+x/D"));s("D3y7"),s("yIBB"),s("XPYc"),s("z+ct"),s("xTPO");var n=function(e){if(e&&e.__esModule)return e;var t={};if(null!=e)for(var s in e)Object.prototype.hasOwnProperty.call(e,s)&&(t[s]=e[s]);return t.default=e,t}(s("JFi+")),a=R(s("qT0E")),o=R(s("vRZA")),r=R(s("fW/A")),l=R(s("i/Md")),d=R(s("t8cq")),u=R(s("oLrn")),c=R(s("47Al")),h=R(s("5G0d")),f=s("anNl"),p=R(s("HOn5")),m=R(s("KloK")),v=R(s("xqHC")),E=(R(s("HH5i")),s("t6J+"));function R(e){return e&&e.__esModule?e:{default:e}}var _=a.default.View.extend({initialize:function(e){var t=this;if(t.options=i.default.extend(!0,t._getDefaultOptions(e),e),t.id=this.options.id,t._event=p.default,t.classNames=o.default,t.dataKeys=u.default,this.$table=(0,i.default)(e.el).addClass(this.classNames.RESTFUL_TABLE).addClass(this.classNames.ALLOW_HOVER).addClass("aui"),this.$table.wrapAll("<form class='aui' action='#' />"),this.$thead=(0,i.default)("<thead/>"),this.$theadRow=(0,i.default)("<tr />").appendTo(this.$thead),this.$tbody=(0,i.default)("<tbody/>"),!this.$table.length)throw new Error("RestfulTable: Init failed! The table you have specified ["+this.$table.selector+"] cannot be found.");if(!this.options.columns)throw new Error("RestfulTable: Init failed! You haven't provided any columns to render.");if(this.options.deleteConfirmationCallback&&!(this.options.deleteConfirmationCallback instanceof Function))throw new Error("RestfulTable: Init failed! deleteConfirmationCallback is not a function");this.showGlobalLoading(),this.options.columns.forEach(function(e){var s=i.default.isFunction(e.header)?e.header():e.header;void 0===s&&(n.warn("You have not specified [header] for column ["+e.id+"]. Using id for now..."),s=e.id),t.$theadRow.append("<th>"+s+"</th>")}),t.$theadRow.append("<th></th><th></th>"),this._models=this._createCollection(),this._rowClass=this.options.views.row,this.editRows=[],this.$table.closest("form").submit(function(e){t.focusedRow&&t.focusedRow.trigger(t._event.SAVE),e.preventDefault()}),this.options.allowReorder&&(this.$theadRow.prepend("<th />"),this.$tbody.sortable({handle:"."+this.classNames.DRAG_HANDLE,helper:function(e,s){var n=(0,i.default)("<div/>").attr("class",s.attr("class")).addClass(t.classNames.MOVEABLE);return s.children().each(function(){var e=(0,i.default)(this),t=parseInt(0+e.css("border-left-width"),10),s=parseInt(0+e.css("border-right-width"),10),a=e[0].clientWidth+t+s;n.append((0,i.default)("<div/>").html(e.html()).attr("class",e.attr("class")).width(a))}),n=(0,i.default)("<div class='aui-restfultable-readonly'/>").append(n),n.css({left:s.offset().left}),n.appendTo(document.body),n},start:function(e,s){var n=s.helper[0].clientHeight,a=s.placeholder.find("td");s.item.addClass(t.classNames.MOVEABLE).children().each(function(e){(0,i.default)(this).width(a.eq(e).width())});var o='<td colspan="'+t.getColumnCount()+'">&nbsp;</td>';s.placeholder.html(o).css({height:n,visibility:"visible"}),t.getRowFromElement(s.item[0]).trigger(t._event.MODAL)},stop:function(e,s){(0,i.default)(s.item[0]).is(":visible")&&(s.item.removeClass(t.classNames.MOVEABLE).children().attr("style",""),s.placeholder.removeClass(t.classNames.ROW),t.getRowFromElement(s.item[0]).trigger(t._event.MODELESS))},update:function(e,s){var i={row:t.getRowFromElement(s.item[0]),item:s.item,nextItem:s.item.next(),prevItem:s.item.prev()};t.move(i)},axis:"y",delay:0,containment:"document",cursor:"move",scroll:!0,zIndex:8e3}),this.$tbody.on("selectstart mousedown",function(e){return!(0,i.default)(e.target).is("."+t.classNames.DRAG_HANDLE)})),!1!==this.options.allowCreate&&(this._createRow=new this.options.views.editRow({columns:this.options.columns,isCreateRow:!0,model:this.options.model.extend({url:function(){return t.options.resources.self}}),cancelAccessKey:this.options.cancelAccessKey,submitAccessKey:this.options.submitAccessKey,allowReorder:this.options.allowReorder,fieldFocusSelector:this.options.fieldFocusSelector}),this._createRow.on(this._event.CREATED,function(e){void 0===t.options.addPosition&&"bottom"===t.options.createPosition||"bottom"===t.options.addPosition?t.addRow(e):t.addRow(e,0)}),this._createRow.on(this._event.VALIDATION_ERROR,function(){this.trigger(t._event.FOCUS)}),this._createRow.render({errors:{},values:{}}),this.$create=(0,i.default)('<tbody class="'+this.classNames.CREATE+'" />').append(this._createRow.el),this._applyFocusCoordinator(this._createRow),this._createRow.trigger(this._event.FOCUS)),this._models.on("remove",function(e){t.getRows().forEach(function(s){s.model===e&&(s.hasFocus()&&t._createRow&&t._createRow.trigger(t._event.FOCUS),t.removeRow(s))})}),this.fetchInitialResources()},fetchInitialResources:function(){var e=this;i.default.isFunction(this.options.resources.all)?this.options.resources.all(function(t){e.populate(t)}):i.default.get(this.options.resources.all,function(t){e.populate(t)})},move:function(e){var t=this,s=function(e){return e.length?{after:t.getRowFromElement(e).model.url()}:{position:"First"}};if(e.row){var n=t.options.reverseOrder?s(e.nextItem):s(e.prevItem);i.default.ajax({url:e.row.model.url()+"/move",type:"POST",dataType:"json",contentType:"application/json",data:JSON.stringify(n),complete:function(){e.row.hideLoading()},success:function(e){(0,f.triggerEvtForInst)(t._event.REORDER_SUCCESS,t,[e])},error:function(e){var s=i.default.parseJSON(e.responseText||e.data);(0,f.triggerEvtForInst)(t._event.SERVER_ERROR,t,[s,e,this])}}),e.row.showLoading()}},_createCollection:function(){var e=this;return new(this.options.Collection.extend({sort:function(t){if(t||(t={}),!this.comparator)throw new Error("Cannot sort a set without a comparator");return this.tableRows=e.getRows(),this.models=this.sortBy(this.comparator,this),this.tableRows=void 0,t.silent||this.trigger("refresh",this,t),this},remove:function(){this.tableRows=e.getRows();for(var t=arguments.length,s=Array(t),i=0;i<t;i++)s[i]=arguments[i];return a.default.Collection.prototype.remove.apply(this,s),this.tableRows=void 0,this}}))([],{comparator:function(t){var s;return(this&&void 0!==this.tableRows?this.tableRows:e.getRows()).some(function(e,i){if(e.model.id===t.id)return s=i,!0}),s}})},populate:function(e){this.options.reverseOrder&&e.reverse(),this.hideGlobalLoading(),e&&e.length?(this._models.reset([],{silent:!0}),this.renderRows(e),this.isEmpty()&&this.showNoEntriesMsg()):this.showNoEntriesMsg(),this.$table.append(this.$thead),"bottom"===this.options.createPosition?this.$table.append(this.$tbody).append(this.$create):this.$table.append(this.$create).append(this.$tbody),this.$table.trigger(this._event.INITIALIZED,[this]),(0,f.triggerEvtForInst)(this._event.INITIALIZED,this,[this]),this.options.autoFocus&&this.$table.find(":input:text:first").focus()},showGlobalLoading:function(){return this.$loading||(this.$loading=(0,i.default)('<div class="aui-restfultable-init"><span class="aui-restfultable-loading">'+E.spinner+this.options.loadingMsg+"</span></div>")),this.$loading.is(":visible")||this.$loading.insertAfter(this.$table),this},hideGlobalLoading:function(){return this.$loading&&this.$loading.remove(),this},addRow:function(e,t){var s,i;if(!e.id)throw new Error("RestfulTable.addRow: to add a row values object must contain an id. Maybe you are not returning it from your restend point?Recieved:"+JSON.stringify(e));return i=new this.options.model(e),s=this._renderRow(i,t),this._models.add(i),this.removeNoEntriesMsg(),(0,f.triggerEvtForInst)(this._event.ROW_ADDED,this,[s,this]),this},removeRow:function(e){this._models.remove(e.model),e.remove(),this.isEmpty()&&this.showNoEntriesMsg(),(0,f.triggerEvtForInst)(this._event.ROW_REMOVED,this,[e,this])},isEmpty:function(){return 0===this._models.length},getModels:function(){return this._models},getTable:function(){return this.$table},getTableBody:function(){return this.$tbody},getCreateRow:function(){return this._createRow},getColumnCount:function(){var e=2;return this.allowReorder&&++e,this.options.columns.length+e},getRowFromElement:function(e){return(0,i.default)(e).data(this.dataKeys.ROW_VIEW)},showNoEntriesMsg:function(){return this.$noEntries&&this.$noEntries.remove(),this.$noEntries=(0,i.default)("<tr>").addClass(this.classNames.NO_ENTRIES).append((0,i.default)("<td>").attr("colspan",this.getColumnCount()).text(this.options.noEntriesMsg)).appendTo(this.$tbody),this},removeNoEntriesMsg:function(){return this.$noEntries&&this._models.length>0&&this.$noEntries.remove(),this},getRows:function(){var e=this,t=[];return this.$tbody.find("."+this.classNames.READ_ONLY).each(function(){var s=(0,i.default)(this).data(e.dataKeys.ROW_VIEW);s&&t.push(s)}),t},_renderRow:function(e,t){var s,i,n=this,a=this.$tbody.find("."+this.classNames.READ_ONLY);return i=new this._rowClass({model:e,columns:this.options.columns,allowEdit:this.options.allowEdit,allowDelete:this.options.allowDelete,allowReorder:this.options.allowReorder,deleteConfirmationCallback:this.options.deleteConfirmationCallback}),this.removeNoEntriesMsg(),i.on(this._event.ROW_EDIT,function(e){(0,f.triggerEvtForInst)(this._event.EDIT_ROW,{},[this,n]),n.edit(this,e)}),s=i.render().$el,-1!==t&&("number"==typeof t&&0!==a.length?s.insertBefore(a[t]):this.$tbody.append(s)),s.data(this.dataKeys.ROW_VIEW,i),i.on(this._event.MODAL,function(){n.$table.removeClass(n.classNames.ALLOW_HOVER),n.$tbody.sortable("disable"),n.getRows().forEach(function(e){n.isRowBeingEdited(e)||e.delegateEvents({})})}),i.on(this._event.MODELESS,function(){n.$table.addClass(n.classNames.ALLOW_HOVER),n.$tbody.sortable("enable"),n.getRows().forEach(function(e){n.isRowBeingEdited(e)||e.delegateEvents()})}),this._applyFocusCoordinator(i),this.trigger(this._event.ROW_INITIALIZED,i),i},isRowBeingEdited:function(e){var t=!1;return this.editRows.some(function(s){if(s.el===e.el)return t=!0,!0}),t},_applyFocusCoordinator:function(e){var t=this;return e.hasFocusBound||(e.hasFocusBound=!0,e.on(this._event.FOCUS,function(){t.focusedRow&&t.focusedRow!==e&&t.focusedRow.trigger(t._event.BLUR),t.focusedRow=e,e instanceof v.default&&t._createRow&&t._createRow.enable()})),this},_removeEditRow:function(e){var t=i.default.inArray(e,this.editRows);return this.editRows.splice(t,1),this},_shiftFocusAfterEdit:function(){return this.editRows.length>0?this.editRows[this.editRows.length-1].trigger(this._event.FOCUS):this._createRow&&this._createRow.trigger(this._event.FOCUS),this},_saveEditRowOnBlur:function(){return this.editRows.length<=1},dismissEditRows:function(){this.editRows.forEach(function(e){e.hasUpdates()||e.trigger(this._event.FINISHED_EDITING)},this)},edit:function(e,t){var s=this,i=new this.options.views.editRow({el:e.el,columns:this.options.columns,isUpdateMode:!0,allowReorder:this.options.allowReorder,fieldFocusSelector:this.options.fieldFocusSelector,model:e.model,cancelAccessKey:this.options.cancelAccessKey,submitAccessKey:this.options.submitAccessKey}),n=e.model.toJSON();return n.update=!0,i.render({errors:{},update:!0,values:n}).on(s._event.UPDATED,function(t,i){s._removeEditRow(this),this.off(),e.render().delegateEvents(),e.trigger(s._event.UPDATED),!1!==i&&s._shiftFocusAfterEdit()}).on(s._event.VALIDATION_ERROR,function(){this.trigger(s._event.FOCUS)}).on(s._event.FINISHED_EDITING,function(){s._removeEditRow(this),e.render().delegateEvents(),this.off()}).on(s._event.CANCEL,function(){s._removeEditRow(this),this.off(),e.render().delegateEvents(),s._shiftFocusAfterEdit()}).on(s._event.BLUR,function(){s.dismissEditRows(),s._saveEditRowOnBlur()&&this.trigger(s._event.SAVE,!1)}),this._applyFocusCoordinator(i),i.trigger(s._event.FOCUS,t),s._createRow&&s._createRow.disable(),this.editRows.push(i),i},renderRows:function(){var e=this,t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:[],s=this._models.comparator,i=[];this._models.comparator=void 0;var n=t.map(function(t){var s=new e.options.model(t);return i.push(e._renderRow(s,-1).el),s});return this._models.add(n,{silent:!0}),this._models.comparator=s,this.removeNoEntriesMsg(),this.$tbody.append(i),this},_getDefaultOptions:function(e){return{model:e.model||h.default,allowEdit:!0,views:{editRow:c.default,row:v.default},Collection:a.default.Collection.extend({url:e.resources.self,model:e.model||h.default}),allowReorder:!1,fieldFocusSelector:function(e){return":input[name="+e+"], #"+e},loadingMsg:e.loadingMsg||"Loading"}}});_.ClassNames=o.default,_.CustomCreateView=r.default,_.CustomEditView=l.default,_.CustomReadView=d.default,_.DataKeys=u.default,_.EditRow=c.default,_.EntryModel=h.default,_.Events=p.default,_.Row=v.default,(0,m.default)("RestfulTable",_),t.default=_,e.exports=t.default},anNl:function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0}),t.triggerEvtForInst=t.triggerEvt=t.bindEvt=void 0;var i=function(e){return e&&e.__esModule?e:{default:e}}(s("+x/D"));var n=document||{},a=(0,i.default)(n);function o(e,t){a.trigger(e,t)}t.bindEvt=function(e,t){a.bind(e,t)},t.triggerEvt=o,t.triggerEvtForInst=function(e,t,s){(0,i.default)(t).trigger(e,s),o(e,s),t.id&&o(t.id+"-"+e,s)}},"fW/A":function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var i=function(e){return e&&e.__esModule?e:{default:e}}(s("qT0E"));t.default=i.default.View,e.exports=t.default},"i/Md":function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var i=function(e){return e&&e.__esModule?e:{default:e}}(s("qT0E"));t.default=i.default.View,e.exports=t.default},lyon:function(e,t){jQuery.fn.serializeObject=function(){var e={};return this.find(":input:not(:button):not(:submit):not(:radio):not('select[multiple]')").each(function(){""!==this.name&&(null===this.value&&(this.value=""),e[this.name]=this.value.match(/^(tru|fals)e$/i)?"true"==this.value.toLowerCase():this.value)}),this.find("input:radio:checked").each(function(){e[this.name]=this.value}),this.find("select[multiple]").each(function(){var t=jQuery(this),s=t.val();t.data("aui-ss")?e[this.name]=s?s[0]:"":e[this.name]=null!==s?s:[]}),e}},oLrn:function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0}),t.default={ENABLED_SUBMIT:"enabledSubmit",ROW_VIEW:"RestfulTable_Row_View"},e.exports=t.default},"t6J+":function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0}),t.spinner=void 0,t.appendStatusSpinner=function(e){0===e.find(a).length&&e.find("."+i.default.STATUS).append(n)},t.removeStatusSpinner=function(e){e.find("."+i.default.STATUS+" "+a).remove()},s("tYoR");var i=function(e){return e&&e.__esModule?e:{default:e}}(s("vRZA"));var n=t.spinner='<aui-spinner size="small"></aui-spinner>',a="aui-spinner"},t8cq:function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var i=function(e){return e&&e.__esModule?e:{default:e}}(s("qT0E"));t.default=i.default.View,e.exports=t.default},vRZA:function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0}),t.default={NO_VALUE:"aui-restfultable-editable-no-value",NO_ENTRIES:"aui-restfultable-no-entires",RESTFUL_TABLE:"aui-restfultable",ROW:"aui-restfultable-row",READ_ONLY:"aui-restfultable-readonly",ACTIVE:"aui-restfultable-active",ALLOW_HOVER:"aui-restfultable-allowhover",FOCUSED:"aui-restfultable-focused",MOVEABLE:"aui-restfultable-movable",DISABLED:"aui-restfultable-disabled",SUBMIT:"aui-restfultable-submit",CANCEL:"aui-restfultable-cancel",EDIT_ROW:"aui-restfultable-editrow",CREATE:"aui-restfultable-create",DRAG_HANDLE:"aui-restfultable-draghandle",ORDER:"aui-restfultable-order",EDITABLE:"aui-restfultable-editable",ERROR:"error",DELETE:"aui-restfultable-delete",STATUS:"aui-restfultable-status"},e.exports=t.default},xqHC:function(e,t,s){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var i=d(s("+x/D")),n=d(s("qT0E")),a=d(s("vRZA")),o=d(s("oLrn")),r=d(s("HOn5")),l=s("t6J+");function d(e){return e&&e.__esModule?e:{default:e}}t.default=n.default.View.extend({tagName:"tr",events:{"click .aui-restfultable-editable":"edit"},initialize:function(e){var t=this;if(e=e||{},this._event=r.default,this.classNames=a.default,this.dataKeys=o.default,this.columns=e.columns,this.allowEdit=e.allowEdit,this.allowDelete=e.allowDelete,!this.events["click .aui-restfultable-editable"])throw new Error("It appears you have overridden the events property. To add events you will need to usea work around. https://github.com/documentcloud/backbone/issues/244");this.index=e.index||0,this.deleteConfirmationCallback=e.deleteConfirmationCallback,this.allowReorder=e.allowReorder,this.$el=(0,i.default)(this.el),this.on(this._event.CANCEL,function(){return t.disabled=!0}).on(this._event.FOCUS,function(e){return t.focus(e)}).on(this._event.BLUR,function(){return t.unfocus()}).on(this._event.MODAL,function(){return t.$el.addClass(t.classNames.ACTIVE)}).on(this._event.MODELESS,function(){return t.$el.removeClass(t.classNames.ACTIVE)})},renderDragHandle:function(){return'<span class="'+this.classNames.DRAG_HANDLE+'"></span></td>'},defaultColumnRenderer:function(e){if(e.value)return document.createTextNode(e.value.toString())},sync:function(e){var t=this;return this.model.addExpand(e),this.showLoading(),this.model.save(e,{success:function(){t.hideLoading().render(),t.trigger(t._event.UPDATED)},error:function(){t.hideLoading()}}),this},refresh:function(e,t){var s=this;return this.showLoading(),this.model.fetch({success:function(){s.hideLoading().render(),e&&e.apply(this,arguments)},error:function(){s.hideLoading(),t&&t.apply(this,arguments)}}),this},hasFocus:function(){return this.$el.hasClass(this.classNames.FOCUSED)},focus:function(){return(0,i.default)(this.el).addClass(this.classNames.FOCUSED),this},unfocus:function(){return(0,i.default)(this.el).removeClass(this.classNames.FOCUSED),this},showLoading:function(){return(0,l.appendStatusSpinner)(this.$el),this},hideLoading:function(){return(0,l.removeStatusSpinner)(this.$el),this},edit:function(e){var t;return t=(0,i.default)(e.target).is("."+this.classNames.EDITABLE)?(0,i.default)(e.target).attr("data-field-name"):(0,i.default)(e.target).closest("."+this.classNames.EDITABLE).attr("data-field-name"),this.trigger(this._event.ROW_EDIT,t),this},renderOperations:function(){var e=this;if(!1!==this.allowDelete)return(0,i.default)("<a href='#' class='aui-button' />").addClass(this.classNames.DELETE).text("Delete").click(function(t){t.preventDefault(),e.destroy()})},destroy:function(){var e=this;if(this.deleteConfirmationCallback){var t=this.deleteConfirmationCallback(this.model.toJSON());if(!t||!t.then)throw new Error("deleteConfirmationCallback needs to return a Promise");t.then(function(){return e.model.destroy()},function(){})}else this.model.destroy()},render:function(){var e=this,t=this.model.toJSON(),s=(0,i.default)("<td class='aui-restfultable-operations' />").append(this.renderOperations({},t)),n=(0,i.default)('<td class="'+this.classNames.STATUS+'" />');return this.$el.removeClass(this.classNames.DISABLED+" "+this.classNames.FOCUSED+" "+this.classNames.EDIT_ROW).addClass(this.classNames.READ_ONLY).empty(),this.allowReorder&&(0,i.default)('<td  class="'+this.classNames.ORDER+'" />').append(this.renderDragHandle()).appendTo(e.$el),this.$el.attr("data-id",this.model.id),i.default.each(this.columns,function(s,n){var a,o=(0,i.default)("<td />"),r=t[n.id],l=n.fieldName||n.id,d=[{name:l,value:r,allowEdit:n.allowEdit},t,e.model];if(r&&e.$el.attr("data-"+n.id,r),a=n.readView?new n.readView({model:e.model}).render(d[0]):e.defaultColumnRenderer.apply(e,d),!1!==e.allowEdit&&!1!==n.allowEdit){var u=(0,i.default)("<span />").addClass(e.classNames.EDITABLE).append('<span class="aui-icon aui-icon-small aui-iconfont-edit"></span>').append(a).attr("data-field-name",l);o=(0,i.default)("<td />").append(u).appendTo(e.$el),a&&i.default.trim(a)||(o.addClass(e.classNames.NO_VALUE),u.html((0,i.default)("<em />").text(this.emptyText||"Enter value")))}else o.append(a);n.styleClass&&o.addClass(n.styleClass),o.appendTo(e.$el)}),this.$el.append(s).append(n).addClass(this.classNames.ROW+" "+this.classNames.READ_ONLY),this.trigger(this._event.RENDER,this.$el,t),this.$el.trigger(this._event.CONTENT_REFRESHED,[this.$el]),this}}),e.exports=t.default}},[["G3cN","runtime","aui.splitchunk.vendors--1df5b34e16","aui.splitchunk.vendors--95c789edf5","aui.splitchunk.vendors--9c48cc20a9","aui.splitchunk.vendors--20a97d6a33","aui.splitchunk.vendors--d18e3cafa7","aui.splitchunk.vendors--db57146687","aui.splitchunk.vendors--51504ebf10","aui.splitchunk.vendors--9c8c8c1546","aui.splitchunk.vendors--351ae504d7","aui.splitchunk.vendors--20e849aab3","aui.splitchunk.vendors--06bc6ae5d7","aui.splitchunk.vendors--6ce18a1d80","aui.splitchunk.vendors--37ccb8d673","aui.splitchunk.172ffb6da7","aui.splitchunk.b0831cc7d0","aui.splitchunk.572a8bf5cd","aui.splitchunk.a16cabd587","aui.splitchunk.fbd1a5ab27","aui.splitchunk.d49cf794d2","aui.splitchunk.54d3f16c20","aui.splitchunk.336ae4f9e7","aui.splitchunk.1659111a3c","aui.splitchunk.1df5b34e16","aui.splitchunk.fb15cffa72","aui.splitchunk.9c48cc20a9","aui.splitchunk.cd8d39be78","aui.splitchunk.ed80e00f15","aui.splitchunk.ed86a19e01","aui.splitchunk.53839a15cf","aui.splitchunk.b2ecdd4179","aui.splitchunk.20e849aab3","aui.splitchunk.16f099a0da"]]]);
//# sourceMappingURL=aui.chunk.7cfb006e493d8523a32c--d5a44e16a3b7bfa2e178.js.map;
;
/* module-key = 'jira.webresources:aui-restfultable-amd-shim', location = '/static/lib/amd-shims/aui-restfultable-amd.js' */
define("aui/restful-table",function(){return AJS.RestfulTable});;
;
/* module-key = 'com.atlassian.jira.jira-project-config-plugin:project-config-restfultable', location = 'global/js/events.js' */
!function(){"use strict";var e=require("jquery"),r=require("aui/restful-table"),o=require("jira/util/events"),i=require("jira/dialog/form-dialog");o.bind(r.Events.SERVER_ERROR,function(r,o){var s=e("#project-config-error-console");o&&o.errorMessages&&(s.empty(),new i({id:"server-error-dialog",content:function(e){e(JIRA.Templates.Common.serverErrorDialog({message:o.errorMessages[0]}))}}).show())})}();;
;
/* module-key = 'vn.com.bng.EffortManagement:Holiday-resources', location = '/templates/soy/holiday.soy' */
// This file was automatically generated from holiday.soy.
// Please don't edit this file by hand.

/**
 * @fileoverview Templates in namespace JIRA.Templates.Holiday.
 */

if (typeof JIRA == 'undefined') { var JIRA = {}; }
if (typeof JIRA.Templates == 'undefined') { JIRA.Templates = {}; }
if (typeof JIRA.Templates.Holiday == 'undefined') { JIRA.Templates.Holiday = {}; }


JIRA.Templates.Holiday.viewUsername = function(opt_data, opt_ignored) {
  return '<div class="jira-user-name user-hover jira-user-avatar" rel="' + soy.$$escapeHtml(opt_data.username) + '" id="project_summary_' + soy.$$escapeHtml(opt_data.username) + '"><span class="aui-avatar aui-avatar-xsmall"><span class="aui-avatar-inner"><img src="/secure/useravatar?size=xsmall&ownerId=' + soy.$$escapeHtml(opt_data.username) + '&avatarId=' + soy.$$escapeHtml(opt_data.avatarId) + '"></span></span>' + soy.$$escapeHtml(opt_data.displayName ? opt_data.displayName : '') + '<input type="hidden" name="lowerUserName" value="' + soy.$$escapeHtml(opt_data.username) + '" /></div>';
};
if (goog.DEBUG) {
  JIRA.Templates.Holiday.viewUsername.soyTemplateName = 'JIRA.Templates.Holiday.viewUsername';
}


JIRA.Templates.Holiday.editUsername = function(opt_data, opt_ignored) {
  return '<div><select class="single-user-picker js-default-user-picker" name="lowerUserName"><option selected="selected" value="' + soy.$$escapeHtml(opt_data.username ? opt_data.username : '') + '">' + soy.$$escapeHtml(opt_data.displayName ? opt_data.displayName : '') + '</option></select></div>';
};
if (goog.DEBUG) {
  JIRA.Templates.Holiday.editUsername.soyTemplateName = 'JIRA.Templates.Holiday.editUsername';
}


JIRA.Templates.Holiday.editView = function(opt_data, opt_ignored) {
  return '<div style="display: inline-block;width:200px"><input class="text textNonForm" style ="width:150px" id="' + soy.$$escapeHtml(opt_data.inputFieldId) + '" name="' + soy.$$escapeHtml(opt_data.inputFieldName) + '" placeholder="' + soy.$$escapeHtml(opt_data.placeholder) + '" type="text" value="' + soy.$$escapeHtml(opt_data.dateValue) + '" /><a href="#" id="' + soy.$$escapeHtml(opt_data.buttonId) + '" name="' + soy.$$escapeHtml(opt_data.buttonName) + '" style="padding-left: 5px;"><span class="aui-icon icon-date"></span></a></div>';
};
if (goog.DEBUG) {
  JIRA.Templates.Holiday.editView.soyTemplateName = 'JIRA.Templates.Holiday.editView';
}


JIRA.Templates.Holiday.editTime = function(opt_data, opt_ignored) {
  return '<input type="text" class="text" name="' + soy.$$escapeHtml(opt_data.name) + '" style ="' + soy.$$escapeHtml(opt_data.style) + '" value="' + soy.$$escapeHtml(opt_data.value) + '">';
};
if (goog.DEBUG) {
  JIRA.Templates.Holiday.editTime.soyTemplateName = 'JIRA.Templates.Holiday.editTime';
}


JIRA.Templates.Holiday.editHolidayType = function(opt_data, opt_ignored) {
  var output = '<form class="aui"><select class="select" name="holidayTypeId">';
  var itemList46 = opt_data.options;
  var itemListLen46 = itemList46.length;
  for (var itemIndex46 = 0; itemIndex46 < itemListLen46; itemIndex46++) {
    var itemData46 = itemList46[itemIndex46];
    output += '<option id=' + soy.$$escapeHtml(itemData46.id) + ' value=' + soy.$$escapeHtml(itemData46.id) + ' ' + ((opt_data.optionCurrent == itemData46.id) ? 'selected="selected"' : '') + '>' + soy.$$escapeHtml(itemData46.type) + '</option>';
  }
  output += '</select></form>';
  return output;
};
if (goog.DEBUG) {
  JIRA.Templates.Holiday.editHolidayType.soyTemplateName = 'JIRA.Templates.Holiday.editHolidayType';
}


JIRA.Templates.Holiday.viewText = function(opt_data, opt_ignored) {
  return '<div name="' + soy.$$escapeHtml(opt_data.name) + '" style="max-width: 240px; white-space: nowrap; text-align: ' + soy.$$escapeHtml(opt_data.align ? opt_data.align : 'left') + ';">' + soy.$$escapeHtml(opt_data.value ? opt_data.value : '') + '</div>';
};
if (goog.DEBUG) {
  JIRA.Templates.Holiday.viewText.soyTemplateName = 'JIRA.Templates.Holiday.viewText';
}
;
;
/* module-key = 'vn.com.bng.EffortManagement:Holiday-resources', location = '/js/holiday.js' */
function renderHolidayTable(isSysAdmin) {
	jQuery('#tbl_holiday').empty()
	var usernameView = AJS.RestfulTable.CustomEditView.extend({
		render : function(args) {
			args.displayName = isSysAdmin ? this.model.get('fullName')
					: getLoggedInUserDisplay();
			args.username = isSysAdmin ? this.model.get('lowerUserName')
					: getLoggedInUserName();
			args.avatarId = isSysAdmin ? this.model.get('avatarId')
					: getLoggedInUserAvatar();
			return JIRA.Templates.Holiday.viewUsername(args);
		}
	});

	var usernameEdit = AJS.RestfulTable.CustomEditView.extend({
		render : function(args) {
			args.username = this.model.get("lowerUserName");
			args.displayName = this.model.get("fullName");
			return JIRA.Templates.Holiday.editUsername(args);
		}
	});

	var StartDateEdit = AJS.RestfulTable.CustomEditView.extend({
		render : function(args) {
			args.inputFieldId = 'fromDate';
			args.inputFieldName = 'fromDate';
			args.buttonId = 'icon-from-date-pick';
			args.buttonName = 'icon-from-date-pick';
			args.placeholder = 'From Date';
			if (this.model.get('fromDate') != undefined)
				args.dateValue = this.model.get('fromDate');
			else
				args.dateValue = "";
			;
			return JIRA.Templates.Holiday.editView(args);
		}
	});
	var ToDateEdit = AJS.RestfulTable.CustomEditView.extend({
		render : function(args) {
			args.inputFieldId = 'toDate';
			args.inputFieldName = 'toDate';
			args.buttonId = 'icon-to-date-pick';
			args.buttonName = 'icon-to-date-pick';
			args.placeholder = 'To Date';
			if (this.model.get('toDate') != undefined)
				args.dateValue = this.model.get('toDate');
			else
				args.dateValue = "";
			return JIRA.Templates.Holiday.editView(args);
		}
	});
//	var TimeEdit = AJS.RestfulTable.CustomEditView.extend({
//		render : function(args) {
//			args.name = "time";
//			args.style = "";
//			if (this.model.get('time') != undefined
//					|| this.model.get('time') != null)
//				args.value = this.model.get('time');
//			else
//				args.value = "";
//			return JIRA.Templates.Holiday.editTime(args);
//		}
//	});
	
	var readRowRest = AJS.RestfulTable.Row.extend({
		initialize : function() {
			var instance = this;
			var from = this.model.get("fromDate");
			var to = this.model.get("toDate");
			var id = this.model.get("id");
			AJS.RestfulTable.Row.prototype.initialize.apply(this, arguments);
			this.bind(this._event.UPDATED, function(el, data) {
				renderTable();
			});
			
		}
	});
	
    var editType = AJS.RestfulTable.CustomEditView.extend({
        render: function (args) {
        	args.optionCurrent = this.model.get('holidayTypeId');
            args.options = getHolidayOptions();
            return JIRA.Templates.Holiday.editHolidayType(args);
        }
    });
    
    var viewType = AJS.RestfulTable.CustomEditView.extend({
        render: function (args) {
        	args.value = this.model.get('holidayType');
        	args.name = 'holidayType';
        	args.align = 'left';
            return JIRA.Templates.Holiday.viewText(args);
        }
    });
    
	var EditRow = AJS.RestfulTable.EditRow.extend({
		initialize : function() {
			var instance = this;
			AJS.RestfulTable.EditRow.prototype.initialize
					.apply(this, arguments);
			this.bind(this._event.RENDER, function(el, data) {
				Calendar.setup({
					singleClick : true,
					align : "Br",
					firstDay : AJS.params.firstDay,
					button : this.$el.find("#icon-from-date-pick")[0],
					inputField : this.$el.find("#fromDate")[0],
					useISO8601WeekNumbers : false, // use ISO8601 date/time
					// standard
					// ifFormat: AJS.params.dateFormat
					ifFormat : dateFormatSystem
				});

				Calendar.setup({
					singleClick : true,
					align : "Br",
					firstDay : AJS.params.firstDay,
					button : this.$el.find("#icon-to-date-pick")[0],
					inputField : this.$el.find("#toDate")[0],
					useISO8601WeekNumbers : false, // use ISO8601 date/time
					// standard
					ifFormat : dateFormatSystem
				});
				createSingleUserPickersMemberJobXX(el);
			});
			
			
		},
		submit : function() {
			AJS.RestfulTable.EditRow.prototype.submit.apply(this, arguments);
		}
	});

	var resultTbl = new AJS.RestfulTable(
			{
				el : jQuery('#tbl_holiday'),
				allowCreate : true,
				allowEdit : true,
				allowDelete : true,
				noEntriesMsg : "No entries found.",
				resources : {
					all : function() {
						var funcCallback = arguments[0];
						loadData(function(data) {
							funcCallback(data);
						}, function() {
							funcCallback([]);
						});
					},
					self : AJS.contextPath() + "/rest/effort/1.0/holiday"
				},
				views : {
					row : readRowRest,
					editRow : EditRow
				},
				columns : [
						{
							id : "lowerUserName",
							fieldName : "lowerUserName",
							header : "<div style='width: 200px; min-width: 200px; max-width: 200px;'>Account</div>",
							allowEdit : isSysAdmin,
							editView : isSysAdmin ? usernameEdit : usernameView,
							readView : usernameView

						},
						{
							id : "fromDate",
							fieldName : "fromDate",
							header : "<div style='width: 150px; min-width: 150px; max-width: 200px;'>From Date</div>",
							allowEdit : true,
							editView : StartDateEdit
						},
						{
							id : "toDate",
							fieldName : "toDate",
							header : "<div style='width: 150px; min-width: 150px; max-width: 200px;'>To Date</div>",
							allowEdit : true,
							editView : ToDateEdit
						},
//						{
//							id : "time",
//							fieldName : "time",
//							header : "<div style='width: 150px; min-width: 150px; max-width: 200px;'>Time(h)</div>",
//							allowEdit : true,
//							editView : TimeEdit
//						},
						{
							id : "holidayOption",
							fieldName : "holidayOption",
							header : "<div style='width: 100px;min-width: 100px;max-width: 150px;'>Holiday Option</div>",
							allowEdit : true,
							editView : editType,
							readView : viewType
						},
						{
							id : "reason",
							fieldName : "reason",
							header : "<div style='width: 100px;min-width: 100px;max-width: 150px;'>Reason</div>",
							allowEdit : true,
						} ]
			});
			
		var createRow = resultTbl.getCreateRow();
		createRow.bind(AJS.RestfulTable.Events.CREATED, function() {
			renderTable();
		});
}

function loadData(fncSuccess, funcError) {
	var milis = 86400000;
	jQuery(".error").remove();
	var filter_account;
	if (isSysAdmin()) {
		filter_account = jQuery("select[name='filter_account']").val() == null ? ''
				: jQuery("select[name='filter_account']").val().toString();
	} else {
		filter_account = jQuery("#filter_account").val();
	}

	var filterFromDate = jQuery("#filter-from-date-picker").val() || "";
	var filterToDate = jQuery("#filter-to-date-picker").val() || "";
	var queryParams = "?account=" + filter_account + "&from=" + filterFromDate
			+ "&to=" + filterToDate;
	var url = AJS.contextPath() + "/rest/effort/1.0/holiday/list" + queryParams;
	AJS.$.ajax({
		url : url,
		type : "GET",
		dataType : "json",
		contentType : "application/json",
		success : function(response) {
			fncSuccess(response);
			response.forEach(function(data, index) {
				var from = data.fromDate;
				var	to = data.toDate;
				var id = data.id;
			
				if (isWeekend(from) &&  ((parseDate(from) == parseDate(to)) || 
						(parseDate(to) - parseDate(from) == milis))){
					jQuery('#tbl_holiday tr[data-id='+id+']').css('background', '#ccc');
					
				}
			});
			
		},
		error : function(error) {
			var errors = JSON.parse(error.responseText);
			$.each(errors.errors, function(key, value) {
				jQuery("#" + key).append(
						"<div class='error'>" + value + "</div>");
			});
			fncSuccess([]);
		},
		complete : function() {

		}
	});
}

function isWeekend(date1) {
	var dt = new Date(date1);

	if (dt.getDay() == 6 || dt.getDay() == 0) {
		return true;
	}
	return false;
}

function parseDate(input) {
	if (input != "") {      
        var d1 = Date.parse(input.toString().replace(/([0-9]+)\/([0-9]+)/,'$2/$1'));
        if (d1 == null) {
           return -1;
        }
       return d1;
    }
}

function createSingleUserPickersMemberJobXX(ctx) {

	var restPath = "/rest/api/1.0/users/picker";

	jQuery(".js-default-user-picker", ctx).each(
			function() {
				var $this = jQuery(this);
				if ($this.data("aui-ss"))
					return;
				var data = {
					showAvatar : true
				}, inputText = $this.data('inputValue');

				new AJS.SingleSelect({
					element : $this,
					submitInputVal : true,
					showDropdownButton : !!$this.data('show-dropdown-button'),
					errorMessage : AJS.I18n.getText("user.picker.invalid.user",
							"'{0}'"),
					ajaxOptions : {
						url : contextPath + restPath,
						query : true, // keep going back to the sever for each
										// keystroke
						data : data,
						formatResponse : JIRA.UserPickerUtil.formatResponse
					},
					inputText : inputText
				});
			});
};