desc "Execute default tasks"
task :default => [ :serve ]

task :serve do
    puts '* Changing the codepage'
    `chcp 65001`
    puts '* Running Jekyll'
    `jekyll serve --watch`
end
