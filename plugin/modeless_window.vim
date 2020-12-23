if exists('g:modeless_window_loaded')
  finish
endif
let g:modeless_window_loaded = 1

command! -bar
  \ ModelessWindow
  \ call modeless_window#run()

augroup modeless_window
  autocmd!
  autocmd VimLeave * call modeless_window#quit()
augroup END
