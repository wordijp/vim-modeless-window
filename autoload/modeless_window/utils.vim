function! modeless_window#utils#settext(txt)
  call s:cls()
  call setline('.', a:txt)
endfunction

" ---

function! s:cls()
  call deletebufline('%', 1, line('$'))
endfunction
