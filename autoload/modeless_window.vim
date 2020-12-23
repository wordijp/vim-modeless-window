" XXX: 一応動くという状態

let s:ch = v:null

let s:send_port = '13578'
let s:recv_port = '13579'

function! modeless_window#run() abort
  call vimproc#system_bg(
    \ 'gvim' .
    \ ' +"set columns=80"' .
    \ ' +"set lines=20"' .
    \ ' +"set titlestring=[MODELESS_WINDOW]"' .
    \ ' +"set bufhidden=hide buftype=nofile noswapfile nobuflisted"' .
    \ ' +"call modeless_window#_recv()"')
endfunction

function! modeless_window#quit()
  " FIXME: Python側で無限ループ待ちしてるので、ソケットを閉じてもPython側のソケットサーバーは生き続ける
  " TODO: いい加減な作りを直す
  if s:ch != v:null
    call ch_close(s:ch)
    let s:ch = v:null
  endif
endfunction

function! modeless_window#send(txt)
  let l:ch = ch_open('127.0.0.1:'.s:send_port)
  let l:st = ch_status(l:ch)
  if l:st ==# 'fail' || l:st ==# 'closed'
  else
    call ch_sendexpr(l:ch, a:txt)
  endif
endfunction

" ---

function! modeless_window#_recv()
  if s:ch == v:null
    let s:ch = ch_open('127.0.0.1:'.s:recv_port, {'close_cb': 'modeless_window#_recv_on_close'})
  endif
  let l:st = ch_status(s:ch)
  if l:st ==# 'fail' || l:st ==# 'closed'
    :q!
    return
  endif
  
  call ch_sendexpr(s:ch, 'message', {'callback': 'modeless_window#_recv_handler'})
endfunction


function! modeless_window#_recv_handler(handle, msg)
  if a:handle ==# 'fail' || a:handle ==# 'closed'
    :q!
    return
  endif

  call modeless_window#utils#settext(a:msg)
  
  " 次へ
  call modeless_window#_recv()
endfunction

function! modeless_window#_recv_on_close(ch)
  " FIXME: Python側にバグがあるので現状ここには来ない
  call ch_close(a:ch)
  :q!
endfunction
