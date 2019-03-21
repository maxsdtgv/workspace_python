/*
Should by placed on the HTTP server
*/
<?php
$verb = strtolower($_SERVER['REQUEST_METHOD']);
$data = array();
switch ($verb)
{
    case 'get':
	$data = $_GET;
	break;
    case 'post':
	$post = file_get_contents('php://input');
	$name='pic.jpg';
	$fp = fopen($name, 'w');
	fwrite($fp, $post);
	fclose($fp);
	break;
    case 'put':
	$name='.'.$_SERVER['REQUEST_URI'];
	$fp = fopen($name, 'w');
	fwrite($fp, file_get_contents('php://input'));
	fclose($fp);
	break;
}
/*
print <<<EOD1
<!DOCTYPE html><html><body><pre>
EOD1;

echo "\r\n<b>Method:</b>\r\n";
print_r($verb);

echo "\r\n<b>POST data:</b>\r\n";
print_r($post);

echo "\r\n<b>GET Data:</b>\r\n";
print_r($data);

echo "\r\n<b>GET file name:</b>\r\n";
print_r($name);
echo "\r\n";

print <<<EOD
</pre></body></html>
EOD;
*/
?>
