$(function() {
  (function () { var script = document.createElement('script'); script.src="//cdn.jsdelivr.net/npm/eruda"; document.body.appendChild(script); script.onload = function () { eruda.init() } })();
  window.onbeforeunload = function (e) { return 0; };
  $('#keywords').tagsInput({ placeholder: '스캔할 키워드' });
  let term = new Terminal({
    convertEol: true,
    fontFamily: `'Fira Mono', monospace`,
    fontSize: 15,
    rendererType: 'dom'
  });
  term.setOption('theme', {
    background: RAW_COLORS.blue[900],
    foreground: COLORS.textOnBackground,
  });
  term.setOption('cursorBlink', true)
  term.open(document.getElementById('terminal'));
  term.resize(Math.floor($('div.container').width() / 9), 15);
  
  term.write('$ ');
  
  eventListener(term);
});

function eventListener(term) {
  let socket = io.connect('https://luftaquila.io', { path: "/brunch-eater/socket" });
  socket.emit('load');
  $('#execute').click(function() {
    
    if($(this).hasClass('green')) {
      $(this).removeClass('green').addClass('red').text('Stop!');
       
      // Verification of inputs
      let keywords = $('#keywords').val(), number = Number($('#number').val());
      if(!keywords.length) return Swal.fire('키워드를 입력하세요.', '', 'error');
      if(number < 0 || !Number.isInteger(number)) return Swal.fire('유효한 숫자가 아닙니다.', '' , 'error');
      
      // Write python command
      let option = '';
      if(keywords.split(',').length > 1) option += ' -m';
      if(number) option += ' -n ' + number;
      
      let payload = {
        command: 'python3',
        file: 'main.py',
        keyword: keywords,
        option: option.trim()
      }
      
      socket.emit('execute', { data: payload });
      term.writeln(payload.command + ' ' +  payload.file + ' -k "' + payload.keyword + '" ' + payload.option);
    }
    else {
      $(this).removeClass('red').addClass('green').text('Run!');
      socket.emit('SIGKILL');
      term.writeln('\n')
    }
  });
  socket.on('progress', function(data) { term.write(data); });
  socket.on('SIGTERM', function(data) { term.write('$ '); socket.emit('load'); });
  socket.on('filelist', function(data) {
    $('#filelist').html('');
    for(let file of data.children.reverse()) {
      $('#filelist').append('' +
        '<li class="file mdc-list-item mdc-ripple-upgraded" data-name="' + file.name + '">' + 
          '<span class="mdc-list-item__text">' +
            '<span class="mdc-list-item__primary-text">' +
              '키워드: ' + file.name.replace('.json', '').split(',', 2)[1] +
            '</span>' +
            '<span class="mdc-list-item__secondary-text">' +
              new Date(file.name.split(',', 2)[0] * 1000).format('yyyy-mm-dd TT h:MM:ss') + 
            '</span>' +  
          '</span>' +
          '<span aria-hidden="true" class="buttonHolder mdc-list-item__meta">' +
            '<button data-mdc-ripple-is-unbounded="" class="view mdc-icon-button material-icons mdc-ripple-upgraded--unbounded mdc-ripple-upgraded" title="" style="--mdc-ripple-fg-size:28px; --mdc-ripple-fg-scale:1.71429; --mdc-ripple-left:10px; --mdc-ripple-top:10px;"><i class="far fa-eye"></i></button>' + 
            '<button data-mdc-ripple-is-unbounded="" class="download mdc-icon-button material-icons mdc-ripple-upgraded--unbounded mdc-ripple-upgraded" title="" style="--mdc-ripple-fg-size:28px; --mdc-ripple-fg-scale:1.71429; --mdc-ripple-left:10px; --mdc-ripple-top:10px;"><i class="fas fa-download"></i></button>' + 
            '<button data-mdc-ripple-is-unbounded="" class="trash mdc-icon-button material-icons mdc-ripple-upgraded--unbounded mdc-ripple-upgraded" title="" style="--mdc-ripple-fg-size:28px; --mdc-ripple-fg-scale:1.71429; --mdc-ripple-left:10px; --mdc-ripple-top:10px;"><i class="far fa-trash-alt"></i></button>' + 
          '</span>' +
        '</li>');
    }
  });
  
  $('#filelist').on('click', '.download', function() {
    let filename = $(this).closest('li').attr('data-name');
    $.ajax({
      url: 'outputs/' + filename,
      type: 'GET',
      dataType: 'json',
      success: function(res) {
        let dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(res));
        let downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", filename);
        document.body.appendChild(downloadAnchorNode); // required for firefox
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
      }
    });
  });
  
  $('#filelist').on('click', '.trash', function() {
    let filename = $(this).closest('li').attr('data-name');
    socket.emit('delete', filename);
  });
  
  $('#filelist').on('click', '.view', function() {
    let filename = $(this).closest('li').attr('data-name');
    $.ajax({
      url: 'outputs/' + filename,
      type: 'GET',
      dataType: 'json',
      success: function(res) {
        Swal.fire('D3 Visualizer', '', 'success');
      }
    });
  });
}

var dateFormat = function () {
  var token = /d{1,4}|m{1,4}|yy(?:yy)?|([HhMsTt])\1?|[LloSZ]|"[^"]*"|'[^']*'/g,
    timezone = /\b(?:[PMCEA][SDP]T|(?:Pacific|Mountain|Central|Eastern|Atlantic) (?:Standard|Daylight|Prevailing) Time|(?:GMT|UTC)(?:[-+]\d{4})?)\b/g,
    timezoneClip = /[^-+\dA-Z]/g,
    pad = function (val, len) {
      val = String(val);
      len = len || 2;
      while (val.length < len) val = "0" + val;
      return val;
    };
  return function (date, mask, utc) {
    var dF = dateFormat;
    if (arguments.length == 1 && Object.prototype.toString.call(date) == "[object String]" && !/\d/.test(date)) {
      mask = date;
      date = undefined;
    }
    date = date ? new Date(date) : new Date;
    if (isNaN(date)) throw SyntaxError("invalid date");
    mask = String(dF.masks[mask] || mask || dF.masks["default"]);
    if (mask.slice(0, 4) == "UTC:") {
      mask = mask.slice(4);
      utc = true;
    }
    var	_ = utc ? "getUTC" : "get",
      d = date[_ + "Date"](),
      D = date[_ + "Day"](),
      m = date[_ + "Month"](),
      y = date[_ + "FullYear"](),
      H = date[_ + "Hours"](),
      M = date[_ + "Minutes"](),
      s = date[_ + "Seconds"](),
      L = date[_ + "Milliseconds"](),
      o = utc ? 0 : date.getTimezoneOffset(),
      flags = {
        d:    d,
        dd:   pad(d),
        ddd:  dF.i18n.dayNames[D],
        dddd: dF.i18n.dayNames[D + 7],
        m:    m + 1,
        mm:   pad(m + 1),
        mmm:  dF.i18n.monthNames[m],
        mmmm: dF.i18n.monthNames[m + 12],
        yy:   String(y).slice(2),
        yyyy: y,
        h:    H % 12 || 12,
        hh:   pad(H % 12 || 12),
        H:    H,
        HH:   pad(H),
        M:    M,
        MM:   pad(M),
        s:    s,
        ss:   pad(s),
        l:    pad(L, 3),
        L:    pad(L > 99 ? Math.round(L / 10) : L),
        t:    H < 12 ? "a"  : "p",
        tt:   H < 12 ? "am" : "pm",
        T:    H < 12 ? "A"  : "P",
        TT:   H < 12 ? "오전" : "오후",
        Z:    utc ? "UTC" : (String(date).match(timezone) || [""]).pop().replace(timezoneClip, ""),
        o:    (o > 0 ? "-" : "+") + pad(Math.floor(Math.abs(o) / 60) * 100 + Math.abs(o) % 60, 4),
        S:    ["th", "st", "nd", "rd"][d % 10 > 3 ? 0 : (d % 100 - d % 10 != 10) * d % 10]
      };
    return mask.replace(token, function ($0) {
      return $0 in flags ? flags[$0] : $0.slice(1, $0.length - 1);
    });
  };
}();
dateFormat.masks = {"default":"ddd mmm dd yyyy HH:MM:ss"};
dateFormat.i18n = {
  dayNames: [
    "일", "월", "화", "수", "목", "금", "토",
    "일요일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"
  ],
  monthNames: [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
  ]
};
Date.prototype.format = function (mask, utc) { return dateFormat(this, mask, utc); };
Date.prototype.getDayNum = function() { return this.getDay() ? this.getDay() : 7; }
