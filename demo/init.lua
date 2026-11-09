local root = assert(vim.env.SLOP_DEMO_ROOT)
vim.opt.rtp:prepend(assert(vim.env.GITSIGNS_RTP))
vim.opt.rtp:prepend(root)
vim.env.PATH = root .. '/tests:' .. vim.env.PATH
vim.o.swapfile = false
vim.o.paste = true
vim.o.number = true
vim.o.termguicolors = true
vim.o.showmode = false
vim.o.laststatus = 2
vim.o.cmdheight = 2
vim.o.signcolumn = 'yes'
vim.o.fillchars = 'eob: '
vim.cmd('colorscheme habamax')
vim.o.statusline = '  slop.nvim  |  %f %m%= %l:%c  '
require('gitsigns').setup({})
require('slop').setup({ mappings = true })
vim.cmd('runtime plugin/slop.lua')
