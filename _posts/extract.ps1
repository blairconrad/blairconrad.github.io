$posts|%{$post = $_;

$date = $post.post_date.SubString(0,10)

$title = $post.title
$filename = $date + "-" + $post.post_name + ".md"
new-item $filename -type file -force

add-content $filename "---`nlayout: post`ntitle: $title`ntags:"
#$post.category | Select '#cdata-section' | % { $tag = $_; add-content $filename "    - $tag" }

foreach ( $category in $post.category )
{
    $tag = ($category | Select-Object -Property @{ Name="tag"; Expression="#cdata-section" }).tag
    add-content $filename "    - $tag"
}

$content = ($post.encoded | Select-Object -Property @{ Name="content"; Expression="#cdata-section" })[0].content
add-content $filename "---`n$content"
}
