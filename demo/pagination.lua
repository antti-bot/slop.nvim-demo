local M = {}

-- Return the visible page of results.
function M.paginate(items, page, size)
  local first = (page - 1) * size + 1
  local last = math.min(first + size - 1, #items)
  local result = {}
  for i = first, last do
    result[#result + 1] = items[i]
  end
  return result
end

-- Format a page label for the status line.
function M.label(page, total)
  return string.format("Page %d of %d", page, total)
end

return M
